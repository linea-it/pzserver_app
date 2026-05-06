import tempfile
import zipfile
from pathlib import Path
from unittest import mock

import yaml
from core.models import (
    Product,
    ProductDownloadArchive,
    ProductDownloadArchiveStatus,
    ProductType,
)
from core.services.product_download import ProductDownloadArchiveService
from core.tasks import build_product_download_archive
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ProductDownloadArchiveServiceTestCase(SimpleTestCase):
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

    def test_download_file_uses_signed_url_without_authentication_header(self):
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
            with override_settings(MEDIA_ROOT=media_root):
                response = self.client.get(
                    f"/api/products/{self.product.pk}/download/file/",
                    {"token": token},
                )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"".join(response.streaming_content), b"ready zip")
        self.assertEqual(
            response["Content-Disposition"],
            "attachment; filename=existing.zip",
        )

    def test_download_file_rejects_invalid_token(self):
        self.client.credentials()
        response = self.client.get(
            f"/api/products/{self.product.pk}/download/file/",
            {"token": "invalid"},
        )

        self.assertEqual(response.status_code, 403)
