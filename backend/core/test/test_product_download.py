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
from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone


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
        self.assertFalse(archive.is_expired)
        self.assertEqual(self.product.download_archives.count(), 1)
        self.assertEqual(self.user.product_download_archives.count(), 1)

    def test_archive_state_helpers(self):
        ready_archive = ProductDownloadArchive.objects.create(
            product=self.product,
            created_by=self.user,
            status=ProductDownloadArchiveStatus.READY,
            filename="ready.zip",
            source_signature="b" * 64,
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        expired_archive = ProductDownloadArchive.objects.create(
            product=self.product,
            created_by=self.user,
            status=ProductDownloadArchiveStatus.READY,
            filename="expired.zip",
            source_signature="c" * 64,
            expires_at=timezone.now() - timezone.timedelta(hours=1),
        )

        self.assertTrue(ready_archive.is_ready)
        self.assertFalse(ready_archive.is_expired)
        self.assertTrue(expired_archive.is_ready)
        self.assertTrue(expired_archive.is_expired)
