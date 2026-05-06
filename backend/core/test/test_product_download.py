import tempfile
import zipfile
from pathlib import Path
from unittest import mock

import yaml
from core.services.product_download import ProductDownloadArchiveService
from django.test import SimpleTestCase, override_settings


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
