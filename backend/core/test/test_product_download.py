import tempfile
import zipfile
from datetime import timedelta
from pathlib import Path
from unittest import mock

import yaml
from core.models import (
    FileRoles,
    Product,
    ProductDownloadArchive,
    ProductDownloadArchiveStatus,
    ProductFile,
    ProductType,
    Release,
)
from core.services.product_download import ProductDownloadArchiveService
from core.tasks import (
    build_product_download_archive,
    build_product_main_file_archive,
    cleanup_product_download_archives,
)
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ProductDownloadArchiveServiceTestCase(TestCase):
    def test_build_zip_preserves_paths_and_embeds_metadata(self):
        with tempfile.TemporaryDirectory() as product_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                product_path = Path(product_dir)
                nested_path = product_path / "nested"
                nested_path.mkdir()

                (product_path / "root.txt").write_text("root", encoding="utf-8")
                (nested_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
                (product_path / "product_metadata.yaml").write_text(
                    "stale: true\n", encoding="utf-8"
                )

                metadata = {
                    "display_name": "Sample Product",
                    "main_file": {"name": "root.txt"},
                }

                zip_path = ProductDownloadArchiveService.build_zip(
                    "sample_product", product_path, metadata, output_dir
                )

                self.assertTrue(zip_path.exists())

                with zipfile.ZipFile(zip_path) as archive:
                    names = archive.namelist()

                    self.assertIn("root.txt", names)
                    self.assertIn("nested/data.csv", names)
                    self.assertIn("product_metadata.yaml", names)
                    self.assertEqual(names.count("product_metadata.yaml"), 1)
                    self.assertEqual(
                        archive.read("nested/data.csv").decode("utf-8"),
                        "a,b\n1,2\n",
                    )

                    archive_metadata = yaml.safe_load(
                        archive.read("product_metadata.yaml").decode("utf-8")
                    )

                self.assertEqual(metadata, archive_metadata)
                self.assertEqual(
                    (product_path / "product_metadata.yaml").read_text(
                        encoding="utf-8"
                    ),
                    "stale: true\n",
                )

    @override_settings(PRODUCT_DOWNLOAD_COMPRESSION_LEVEL=3)
    def test_build_zip_uses_configured_compression_level(self):
        with tempfile.TemporaryDirectory() as product_dir:
            with tempfile.TemporaryDirectory() as output_dir:
                product_path = Path(product_dir)

                with mock.patch("zipfile.ZipFile") as zip_file_mock:
                    ProductDownloadArchiveService.build_zip(
                        "sample_product", product_path, {}, output_dir
                    )

                self.assertEqual(
                    zip_file_mock.call_args.kwargs["compresslevel"],
                    3,
                )

    def test_build_source_snapshot_uses_only_files_included_in_archive(self):
        with tempfile.TemporaryDirectory() as product_dir:
            product_path = Path(product_dir)
            nested_path = product_path / "nested"
            nested_path.mkdir()

            (product_path / "root.txt").write_text("root", encoding="utf-8")
            (nested_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
            (product_path / "product_metadata.yaml").write_text(
                "stale: true\n", encoding="utf-8"
            )

            snapshot = ProductDownloadArchiveService.build_source_snapshot(
                product_path
            )

        self.assertEqual(
            [entry["path"] for entry in snapshot],
            ["nested/data.csv", "root.txt"],
        )
        for entry in snapshot:
            self.assertEqual(
                set(entry.keys()),
                {"path", "size", "mtime_ns"},
            )

    def test_build_source_signature_changes_when_source_files_change(self):
        with tempfile.TemporaryDirectory() as product_dir:
            product_path = Path(product_dir)
            source_file = product_path / "data.csv"
            metadata_file = product_path / "product_metadata.yaml"

            source_file.write_text("a,b\n1,2\n", encoding="utf-8")
            metadata_file.write_text("stale: true\n", encoding="utf-8")

            original_signature = ProductDownloadArchiveService.build_source_signature(
                product_path
            )

            metadata_file.write_text("stale: false\n", encoding="utf-8")
            metadata_signature = ProductDownloadArchiveService.build_source_signature(
                product_path
            )

            source_file.write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
            changed_signature = ProductDownloadArchiveService.build_source_signature(
                product_path
            )

        self.assertEqual(original_signature, metadata_signature)
        self.assertNotEqual(original_signature, changed_signature)

    def test_get_archive_internal_redirect_path_uses_download_root(self):
        with tempfile.TemporaryDirectory() as media_root:
            archive = mock.Mock(
                archive_path="downloads/products/1/file name.zip"
            )

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                internal_path = (
                    ProductDownloadArchiveService.get_archive_internal_redirect_path(
                        archive
                    )
                )

        self.assertEqual(
            internal_path,
            "/internal-downloads/products/1/file%20name.zip",
        )

    def test_find_ready_archive_reuses_expired_archive_until_cleanup(self):
        user = User.objects.create_user(
            username="john", email="john@snow.com", password="you_know_nothing"
        )
        product_type = ProductType.objects.create(
            name="validation_results",
            display_name="Validation Results",
            description="Validation product type.",
        )
        product = Product.objects.create(
            product_type=product_type,
            user=user,
            internal_name="sample_product",
            display_name="Sample Product",
            path="validation_results/sample_product",
        )

        with tempfile.TemporaryDirectory() as media_root:
            product_path = Path(media_root) / product.path
            product_path.mkdir(parents=True)
            (product_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            archive_relative_path = Path(
                f"downloads/products/{product.pk}/expired.zip"
            )
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ARCHIVE_EXPIRE_HOURS=1,
            ):
                source_signature = ProductDownloadArchiveService.build_source_signature(
                    product_path
                )
                expired_archive = ProductDownloadArchive.objects.create(
                    product=product,
                    created_by=user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path=archive_relative_path.as_posix(),
                    filename="expired.zip",
                    size=archive_path.stat().st_size,
                    checksum="a" * 64,
                    source_signature=source_signature,
                    source_updated_at=timezone.now() - timedelta(hours=2),
                )

                result = ProductDownloadArchiveService.find_ready_archive(
                    product, source_signature
                )

                self.assertEqual(result, expired_archive)
                self.assertTrue(archive_path.exists())
                self.assertTrue(
                    ProductDownloadArchive.objects.filter(pk=expired_archive.pk).exists()
                )


class ProductDownloadArchiveModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john", email="john@snow.com", password="you_know_nothing"
        )
        self.product_type = ProductType.objects.create(
            name="validation_results",
            display_name="Validation Results",
            description="Validation product type.",
        )
        self.product = Product.objects.create(
            product_type=self.product_type,
            user=self.user,
            internal_name="sample_product",
            display_name="Sample Product",
            path="validation_results/sample_product",
        )

    def test_archive_defaults_to_pending_status(self):
        archive = ProductDownloadArchive.objects.create(
            product=self.product,
            created_by=self.user,
            filename="sample_product.zip",
            source_signature="a" * 64,
        )

        self.assertEqual(archive.status, ProductDownloadArchiveStatus.PENDING)
        self.assertFalse(archive.is_ready)
        self.assertEqual(self.product.download_archives.count(), 1)
        self.assertEqual(self.user.product_download_archives.count(), 1)

    def test_archive_state_helpers(self):
        ready_archive = ProductDownloadArchive.objects.create(
            product=self.product,
            created_by=self.user,
            status=ProductDownloadArchiveStatus.READY,
            filename="ready.zip",
            source_signature="b" * 64,
        )

        self.assertTrue(ready_archive.is_ready)

    def test_cleanup_product_archives_removes_obsolete_records_and_files(self):
        with tempfile.TemporaryDirectory() as media_root:
            product_path = Path(media_root) / self.product.path
            product_path.mkdir(parents=True)
            (product_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            download_root = Path(media_root) / "downloads"
            archive_dir = download_root / "products" / str(self.product.pk)
            archive_dir.mkdir(parents=True)

            duplicate_path = archive_dir / "duplicate.zip"
            duplicate_path.write_bytes(b"duplicate")
            keep_path = archive_dir / "keep.zip"
            keep_path.write_bytes(b"keep")
            old_path = archive_dir / "old.zip"
            old_path.write_bytes(b"old")

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=download_root,
            ):
                current_signature = (
                    ProductDownloadArchiveService.build_source_signature(product_path)
                )
                duplicate_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path="downloads/products/1/duplicate.zip",
                    filename="duplicate.zip",
                    source_signature=current_signature,
                )
                keep_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path="downloads/products/1/keep.zip",
                    filename="keep.zip",
                    source_signature=current_signature,
                )
                old_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path="downloads/products/1/old.zip",
                    filename="old.zip",
                    source_signature="a" * 64,
                )
                failed_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.FAILED,
                    filename="failed.zip",
                    source_signature=current_signature,
                )
                pending_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.PENDING,
                    filename="pending.zip",
                    source_signature=current_signature,
                )

                result = ProductDownloadArchiveService.cleanup_product_archives(
                    self.product
                )

            self.assertEqual(result["deleted_archives"], 3)
            self.assertEqual(result["deleted_files"], 2)
            self.assertFalse(duplicate_path.exists())
            self.assertFalse(old_path.exists())
            self.assertTrue(keep_path.exists())
            self.assertFalse(
                ProductDownloadArchive.objects.filter(pk=duplicate_archive.pk).exists()
            )
            self.assertFalse(
                ProductDownloadArchive.objects.filter(pk=old_archive.pk).exists()
            )
            self.assertFalse(
                ProductDownloadArchive.objects.filter(pk=failed_archive.pk).exists()
            )
            self.assertTrue(
                ProductDownloadArchive.objects.filter(pk=keep_archive.pk).exists()
            )
            self.assertTrue(
                ProductDownloadArchive.objects.filter(pk=pending_archive.pk).exists()
            )

    def test_cleanup_product_archives_removes_expired_current_archive(self):
        with tempfile.TemporaryDirectory() as media_root:
            product_path = Path(media_root) / self.product.path
            product_path.mkdir(parents=True)
            (product_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            archive_relative_path = Path(
                f"downloads/products/{self.product.pk}/expired.zip"
            )
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ARCHIVE_EXPIRE_HOURS=1,
            ):
                current_signature = (
                    ProductDownloadArchiveService.build_source_signature(product_path)
                )
                expired_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path=archive_relative_path.as_posix(),
                    filename="expired.zip",
                    source_signature=current_signature,
                    source_updated_at=timezone.now() - timedelta(hours=2),
                )

                result = ProductDownloadArchiveService.cleanup_product_archives(
                    self.product
                )

        self.assertEqual(result["deleted_archives"], 1)
        self.assertEqual(result["deleted_files"], 1)
        self.assertFalse(archive_path.exists())
        self.assertFalse(
            ProductDownloadArchive.objects.filter(pk=expired_archive.pk).exists()
        )

    def test_build_product_download_archive_task_marks_archive_ready(self):
        with tempfile.TemporaryDirectory() as media_root:
            download_root = Path(media_root) / "downloads"
            product_path = Path(media_root) / self.product.path
            product_path.mkdir(parents=True)
            (product_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=download_root,
            ):
                archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    filename="pending.zip",
                    source_signature="0" * 64,
                )

                result = build_product_download_archive(archive.pk)

                archive.refresh_from_db()
                archive_path = Path(media_root) / archive.archive_path

                self.assertEqual(result["archive_id"], archive.pk)
                self.assertEqual(archive.status, ProductDownloadArchiveStatus.READY)
                self.assertTrue(archive_path.exists())
                self.assertEqual(archive.filename, archive_path.name)
                self.assertGreater(archive.size, 0)
                self.assertEqual(len(archive.checksum), 64)
                self.assertNotEqual(archive.source_signature, "0" * 64)
                self.assertIsNotNone(archive.source_updated_at)

                with zipfile.ZipFile(archive_path) as zip_file:
                    self.assertIn("data.csv", zip_file.namelist())
                    self.assertIn("product_metadata.yaml", zip_file.namelist())

    def test_build_product_main_file_archive_task_caches_regular_file(self):
        with tempfile.TemporaryDirectory() as media_root:
            download_root = Path(media_root) / "downloads"
            product_path = Path(media_root) / self.product.path
            product_path.mkdir(parents=True)
            data_path = product_path / "data.csv"
            data_path.write_text("a,b\n1,2\n", encoding="utf-8")

            ProductFile.objects.create(
                product=self.product,
                role=FileRoles.MAIN,
                name="data.csv",
                type="text/csv",
                extension=".csv",
                size=data_path.stat().st_size,
                file=f"{self.product.path}/data.csv",
                is_directory=False,
            )

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=download_root,
            ):
                archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    filename="data.csv",
                    source_signature="0" * 64,
                )

                result = build_product_main_file_archive(archive.pk)

                archive.refresh_from_db()
                archive_path = Path(media_root) / archive.archive_path
                cached_content = archive_path.read_text(encoding="utf-8")

        self.assertEqual(result["archive_id"], archive.pk)
        self.assertEqual(archive.status, ProductDownloadArchiveStatus.READY)
        self.assertEqual(archive.filename, "data.csv")
        self.assertEqual(cached_content, "a,b\n1,2\n")
        self.assertEqual(
            archive.archive_path,
            f"downloads/main-files/{self.product.pk}/data.csv",
        )
        self.assertEqual(len(archive.checksum), 64)
        self.assertNotEqual(archive.source_signature, "0" * 64)

    def test_build_product_main_file_archive_task_zips_directory(self):
        with tempfile.TemporaryDirectory() as media_root:
            download_root = Path(media_root) / "downloads"
            product_path = Path(media_root) / self.product.path
            hats_path = product_path / "hats_catalog"
            data_path = hats_path / "dataset" / "Norder=0" / "Dir=0"
            data_path.mkdir(parents=True)
            (hats_path / "collection.properties").write_text(
                "catalog_name=hats_catalog\n",
                encoding="utf-8",
            )
            (data_path / "Npix=0.parquet").write_bytes(b"parquet")

            ProductFile.objects.create(
                product=self.product,
                role=FileRoles.MAIN,
                name="hats_catalog",
                type="application/x-hats",
                extension="",
                size=0,
                file=f"{self.product.path}/hats_catalog",
                is_directory=True,
            )

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=download_root,
            ):
                archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    filename="hats_catalog.zip",
                    source_signature="0" * 64,
                )

                result = build_product_main_file_archive(archive.pk)

                archive.refresh_from_db()
                archive_path = Path(media_root) / archive.archive_path

                with zipfile.ZipFile(archive_path) as zip_file:
                    names = sorted(zip_file.namelist())

        self.assertEqual(result["archive_id"], archive.pk)
        self.assertEqual(archive.status, ProductDownloadArchiveStatus.READY)
        self.assertEqual(archive.filename, "hats_catalog.zip")
        self.assertEqual(
            archive.archive_path,
            f"downloads/main-files/{self.product.pk}/hats_catalog.zip",
        )
        self.assertEqual(
            names,
            [
                "collection.properties",
                "dataset/Norder=0/Dir=0/Npix=0.parquet",
            ],
        )

    def test_build_product_download_archive_task_marks_archive_failed(self):
        archive = ProductDownloadArchive.objects.create(
            product=self.product,
            created_by=self.user,
            filename="pending.zip",
            source_signature="0" * 64,
        )

        with mock.patch.object(
            ProductDownloadArchiveService,
            "prepare_archive",
            side_effect=ValueError("zip failed"),
        ):
            with self.assertRaises(ValueError):
                build_product_download_archive(archive.pk)

        archive.refresh_from_db()

        self.assertEqual(archive.status, ProductDownloadArchiveStatus.FAILED)
        self.assertEqual(archive.error_message, "zip failed")

    def test_cleanup_product_download_archives_task_returns_cleanup_result(self):
        with mock.patch.object(
            ProductDownloadArchiveService,
            "cleanup_obsolete_archives",
            return_value={"deleted_archives": 2, "deleted_files": 1},
        ) as cleanup_mock:
            result = cleanup_product_download_archives()

        self.assertEqual(result, {"deleted_archives": 2, "deleted_files": 1})
        cleanup_mock.assert_called_once_with()


class ProductDownloadArchiveEndpointTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john", email="john@snow.com", password="you_know_nothing"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.product_type = ProductType.objects.create(
            name="validation_results",
            display_name="Validation Results",
            description="Validation product type.",
        )
        self.product = Product.objects.create(
            product_type=self.product_type,
            user=self.user,
            internal_name="sample_product",
            display_name="Sample Product",
            path="validation_results/sample_product",
        )

    def create_product_source_file(self, media_root):
        product_path = Path(media_root) / self.product.path
        product_path.mkdir(parents=True)
        (product_path / "data.csv").write_text("a,b\n1,2\n", encoding="utf-8")
        return product_path

    def create_product_main_file(self, media_root):
        product_path = self.create_product_source_file(media_root)
        data_path = product_path / "data.csv"

        ProductFile.objects.create(
            product=self.product,
            role=FileRoles.MAIN,
            name="data.csv",
            type="text/csv",
            extension=".csv",
            size=data_path.stat().st_size,
            file=f"{self.product.path}/data.csv",
            is_directory=False,
        )

        return data_path

    def create_hats_main_file(self, media_root):
        product_path = Path(media_root) / self.product.path
        hats_path = product_path / "hats_catalog"
        data_path = hats_path / "dataset" / "Norder=0" / "Dir=0"
        data_path.mkdir(parents=True)

        (hats_path / "collection.properties").write_text(
            "catalog_name=hats_catalog\n",
            encoding="utf-8",
        )
        (data_path / "Npix=0.parquet").write_bytes(b"parquet")

        ProductFile.objects.create(
            product=self.product,
            role=FileRoles.MAIN,
            name="hats_catalog",
            type="application/x-hats",
            extension="",
            size=0,
            file=f"{self.product.path}/hats_catalog",
            is_directory=True,
        )

        return hats_path

    def test_download_prepare_creates_archive_and_queues_task(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_source_file(media_root)

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS=0,
            ):
                with mock.patch(
                    "core.views.product.build_product_download_archive.delay"
                ) as delay_mock:
                    delay_mock.return_value.id = "task-1"

                    response = self.client.post(
                        f"/api/products/{self.product.pk}/download/prepare/"
                    )

        archive = ProductDownloadArchive.objects.get(product=self.product)

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["id"], archive.pk)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.PENDING)
        self.assertEqual(archive.task_id, "task-1")
        self.assertEqual(archive.created_by, self.user)
        delay_mock.assert_called_once_with(archive.pk)

    def test_download_prepare_can_wait_until_archive_is_ready(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_source_file(media_root)
            archive_relative_path = Path("downloads/products/1/finished.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            def mark_archive_ready(archive):
                archive.status = ProductDownloadArchiveStatus.READY
                archive.archive_path = archive_relative_path.as_posix()
                archive.filename = "finished.zip"
                archive.size = archive_path.stat().st_size
                archive.checksum = "a" * 64
                archive.save(
                    update_fields=[
                        "status",
                        "archive_path",
                        "filename",
                        "size",
                        "checksum",
                        "updated_at",
                    ]
                )
                return archive

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS=10,
                PRODUCT_DOWNLOAD_PREPARE_POLL_INTERVAL_SECONDS=0,
            ):
                with mock.patch(
                    "core.views.product.build_product_download_archive.delay"
                ) as delay_mock:
                    delay_mock.return_value.id = "task-1"

                    with mock.patch(
                        "core.services.product_download.time.sleep",
                        side_effect=lambda seconds: mark_archive_ready(
                            ProductDownloadArchive.objects.get(product=self.product)
                        ),
                    ):
                        response = self.client.post(
                            f"/api/products/{self.product.pk}/download/prepare/"
                        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.READY)
        self.assertIn("download_url", response.data)

    def test_download_prepare_reuses_ready_archive(self):
        with tempfile.TemporaryDirectory() as media_root:
            product_path = self.create_product_source_file(media_root)
            archive_relative_path = Path("downloads/products/1/existing.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            with override_settings(MEDIA_ROOT=media_root):
                source_signature = (
                    ProductDownloadArchiveService.build_source_signature(product_path)
                )
                archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path=archive_relative_path.as_posix(),
                    filename="existing.zip",
                    size=archive_path.stat().st_size,
                    checksum="a" * 64,
                    source_signature=source_signature,
                )

                with mock.patch(
                    "core.views.product.build_product_download_archive.delay"
                ) as delay_mock:
                    response = self.client.post(
                        f"/api/products/{self.product.pk}/download/prepare/"
                    )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], archive.pk)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.READY)
        self.assertIn("download_url", response.data)
        self.assertIn("expired_time", response.data)
        delay_mock.assert_not_called()

    def test_download_prepare_reuses_ready_archive_until_cleanup_even_when_expired(self):
        with tempfile.TemporaryDirectory() as media_root:
            product_path = self.create_product_source_file(media_root)
            archive_relative_path = Path("downloads/products/1/expired.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ARCHIVE_EXPIRE_HOURS=1,
                PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS=0,
            ):
                source_signature = (
                    ProductDownloadArchiveService.build_source_signature(product_path)
                )
                expired_archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path=archive_relative_path.as_posix(),
                    filename="expired.zip",
                    size=archive_path.stat().st_size,
                    checksum="a" * 64,
                    source_signature=source_signature,
                    source_updated_at=timezone.now() - timedelta(hours=2),
                )

                with mock.patch(
                    "core.views.product.build_product_download_archive.delay"
                ) as delay_mock:
                    response = self.client.post(
                        f"/api/products/{self.product.pk}/download/prepare/"
                    )

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.data["id"], expired_archive.pk)
                self.assertEqual(
                    response.data["status"], ProductDownloadArchiveStatus.READY
                )
                self.assertIn("download_url", response.data)
                self.assertIn("expired_time", response.data)
                self.assertTrue(
                    ProductDownloadArchive.objects.filter(pk=expired_archive.pk).exists()
                )
                self.assertTrue(archive_path.exists())
                delay_mock.assert_not_called()

    def test_download_status_returns_not_found_when_no_archive_matches_signature(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_source_file(media_root)

            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/status/"
                )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "not_found")

    def test_download_file_uses_signed_url_with_authenticated_user(self):
        with tempfile.TemporaryDirectory() as media_root:
            archive_relative_path = Path("downloads/products/1/existing.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")
            archive_size = archive_path.stat().st_size

            archive = ProductDownloadArchive.objects.create(
                product=self.product,
                created_by=self.user,
                status=ProductDownloadArchiveStatus.READY,
                archive_path=archive_relative_path.as_posix(),
                filename="existing.zip",
                size=archive_path.stat().st_size,
                checksum="a" * 64,
                source_signature="b" * 64,
            )
            token = ProductDownloadArchiveService.build_download_token(
                archive, self.user
            )

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/file/",
                    {"token": token},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["X-Accel-Redirect"],
            "/internal-downloads/products/1/existing.zip",
        )
        self.assertEqual(response["Content-Length"], str(archive_size))
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=existing.zip",
        )

    def test_download_file_rejects_unauthenticated_request_even_with_valid_token(self):
        with tempfile.TemporaryDirectory() as media_root:
            archive_relative_path = Path("downloads/products/1/existing.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            archive = ProductDownloadArchive.objects.create(
                product=self.product,
                created_by=self.user,
                status=ProductDownloadArchiveStatus.READY,
                archive_path=archive_relative_path.as_posix(),
                filename="existing.zip",
                size=archive_path.stat().st_size,
                checksum="a" * 64,
                source_signature="b" * 64,
            )
            token = ProductDownloadArchiveService.build_download_token(
                archive, self.user
            )

            self.client.credentials()
            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/file/",
                    {"token": token},
                )

        self.assertIn(response.status_code, [401, 403])

    def test_download_file_accepts_token_generated_for_another_user_with_access(self):
        with tempfile.TemporaryDirectory() as media_root:
            archive_relative_path = Path("downloads/products/1/existing.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            archive = ProductDownloadArchive.objects.create(
                product=self.product,
                created_by=self.user,
                status=ProductDownloadArchiveStatus.READY,
                archive_path=archive_relative_path.as_posix(),
                filename="existing.zip",
                size=archive_path.stat().st_size,
                checksum="a" * 64,
                source_signature="b" * 64,
            )
            another_user = User.objects.create_user(
                username="ygritte",
                email="ygritte@north.com",
                password="you_know_nothing",
            )
            token = ProductDownloadArchiveService.build_download_token(
                archive, another_user
            )

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/file/",
                    {"token": token},
                )

        self.assertEqual(response.status_code, 200)

    def test_download_file_rejects_authenticated_user_without_product_access(self):
        restricted_group = Group.objects.create(name="release-group-restricted")
        restricted_release = Release.objects.create(
            name="release-restricted",
            display_name="Release Restricted",
            description="Restricted release.",
            indexing_column="id",
            has_mag_hats=False,
            has_flux_hats=True,
            is_public=False,
        )
        restricted_release.access_groups.add(restricted_group)
        self.product.release = restricted_release
        self.product.save(update_fields=["release", "updated_at"])

        blocked_user = User.objects.create_user(
            username="blocked_user",
            email="blocked@north.com",
            password="you_know_nothing",
        )
        blocked_token = Token.objects.create(user=blocked_user)

        with tempfile.TemporaryDirectory() as media_root:
            archive_relative_path = Path("downloads/products/1/existing.zip")
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_bytes(b"ready zip")

            archive = ProductDownloadArchive.objects.create(
                product=self.product,
                created_by=self.user,
                status=ProductDownloadArchiveStatus.READY,
                archive_path=archive_relative_path.as_posix(),
                filename="existing.zip",
                size=archive_path.stat().st_size,
                checksum="a" * 64,
                source_signature="b" * 64,
            )
            token = ProductDownloadArchiveService.build_download_token(
                archive, self.user
            )

            self.client.credentials(
                HTTP_AUTHORIZATION="Token " + blocked_token.key
            )
            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/file/",
                    {"token": token},
                )

        self.assertEqual(response.status_code, 404)

    def test_download_file_rejects_invalid_token(self):
        response = self.client.get(
            f"/api/products/{self.product.pk}/download/file/",
            {"token": "invalid"},
        )

        self.assertEqual(response.status_code, 403)

    def test_legacy_download_endpoint_includes_deprecation_headers(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_source_file(media_root)

            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/"
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Deprecation"], "true")
        self.assertIn(
            f"/api/products/{self.product.pk}/download/prepare/",
            response["Link"],
        )

    def test_download_main_file_prepare_caches_regular_file_synchronously(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_main_file(media_root)

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
                PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS=0,
            ):
                source_signature = (
                    ProductDownloadArchiveService.build_main_file_source_signature(
                        self.product
                    )
                )
                with mock.patch(
                    "core.views.product.build_product_main_file_archive.delay"
                ) as delay_mock:
                    response = self.client.post(
                        f"/api/products/{self.product.pk}/download/main-file/prepare/"
                    )
                    cached_path = (
                        Path(media_root)
                        / "downloads"
                        / "main-files"
                        / str(self.product.pk)
                        / "data.csv"
                    )
                    cached_content = cached_path.read_text(encoding="utf-8")

        archive = ProductDownloadArchive.objects.get(product=self.product)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], archive.pk)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.READY)
        self.assertIsNone(archive.task_id)
        self.assertEqual(archive.filename, "data.csv")
        self.assertEqual(archive.source_signature, source_signature)
        self.assertEqual(cached_content, "a,b\n1,2\n")
        self.assertIn("/download/main-file/file/", response.data["download_url"])
        delay_mock.assert_not_called()

    def test_download_main_file_prepare_queues_task_for_hats_directory(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_hats_main_file(media_root)

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
                PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS=0,
            ):
                source_signature = (
                    ProductDownloadArchiveService.build_main_file_source_signature(
                        self.product
                    )
                )
                with mock.patch(
                    "core.views.product.build_product_main_file_archive.delay"
                ) as delay_mock:
                    delay_mock.return_value.id = "main-task-1"

                    response = self.client.post(
                        f"/api/products/{self.product.pk}/download/main-file/prepare/"
                    )

        archive = ProductDownloadArchive.objects.get(product=self.product)

        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["id"], archive.pk)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.PENDING)
        self.assertEqual(archive.task_id, "main-task-1")
        self.assertEqual(archive.filename, "hats_catalog.zip")
        self.assertEqual(archive.source_signature, source_signature)
        delay_mock.assert_called_once_with(archive.pk)

    def test_download_main_file_prepare_reuses_ready_archive(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_main_file(media_root)
            archive_relative_path = Path(
                f"downloads/main-files/{self.product.pk}/data.csv"
            )
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_text("a,b\n1,2\n", encoding="utf-8")

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                source_signature = (
                    ProductDownloadArchiveService.build_main_file_source_signature(
                        self.product
                    )
                )
                archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path=archive_relative_path.as_posix(),
                    filename="data.csv",
                    size=archive_path.stat().st_size,
                    checksum="a" * 64,
                    source_signature=source_signature,
                )

                with mock.patch(
                    "core.views.product.build_product_main_file_archive.delay"
                ) as delay_mock:
                    response = self.client.post(
                        f"/api/products/{self.product.pk}/download/main-file/prepare/"
                    )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], archive.pk)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.READY)
        self.assertIn("/download/main-file/file/", response.data["download_url"])
        delay_mock.assert_not_called()

    def test_download_main_file_status_returns_not_found_when_no_archive_matches(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_product_main_file(media_root)

            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/main-file/status/"
                )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data["status"], "not_found")

    def test_download_main_file_file_uses_internal_redirect_for_regular_file(self):
        with tempfile.TemporaryDirectory() as media_root:
            data_path = self.create_product_main_file(media_root)
            data_size = data_path.stat().st_size
            archive_relative_path = Path(
                f"downloads/main-files/{self.product.pk}/data.csv"
            )
            archive_path = Path(media_root) / archive_relative_path
            archive_path.parent.mkdir(parents=True)
            archive_path.write_text(
                data_path.read_text(encoding="utf-8"),
                encoding="utf-8",
            )

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
            ):
                source_signature = (
                    ProductDownloadArchiveService.build_main_file_source_signature(
                        self.product
                    )
                )
                archive = ProductDownloadArchive.objects.create(
                    product=self.product,
                    created_by=self.user,
                    status=ProductDownloadArchiveStatus.READY,
                    archive_path=archive_relative_path.as_posix(),
                    filename="data.csv",
                    size=archive_path.stat().st_size,
                    checksum="a" * 64,
                    source_signature=source_signature,
                )
                token = ProductDownloadArchiveService.build_download_token(
                    archive, self.user
                )
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/main-file/file/",
                    {"token": token},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Length"], str(data_size))
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=data.csv",
        )
        self.assertEqual(
            response["X-Accel-Redirect"],
            f"/internal-downloads/main-files/{self.product.pk}/data.csv",
        )

    def test_download_main_file_legacy_endpoint_returns_accepted_while_task_runs(self):
        with tempfile.TemporaryDirectory() as media_root:
            self.create_hats_main_file(media_root)

            with override_settings(
                MEDIA_ROOT=media_root,
                PRODUCT_DOWNLOAD_ROOT=Path(media_root) / "downloads",
                PRODUCT_DOWNLOAD_INTERNAL_URL="/internal-downloads/",
                PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS=0,
            ):
                zip_path = (
                    Path(media_root)
                    / "downloads"
                    / "main-files"
                    / str(self.product.pk)
                    / "hats_catalog.zip"
                )
                with mock.patch(
                    "core.views.product.build_product_main_file_archive.delay"
                ) as delay_mock:
                    delay_mock.return_value.id = "main-task-1"

                    response = self.client.get(
                        f"/api/products/{self.product.pk}/download_main_file/"
                    )
                    zip_exists = zip_path.exists()

        archive = ProductDownloadArchive.objects.get(product=self.product)
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.data["id"], archive.pk)
        self.assertEqual(response.data["status"], ProductDownloadArchiveStatus.PENDING)
        self.assertFalse(zip_exists)
        delay_mock.assert_called_once_with(archive.pk)
