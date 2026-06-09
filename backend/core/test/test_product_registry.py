import json
import mimetypes
import sys
import tarfile
import tempfile
import types
import zipfile
from pathlib import Path
from unittest import mock

import pandas as pd
from core.models import Product, ProductFile, ProductType, Release
from core.product_handle import ProductHandle
from core.product_steps import RegistryProduct
from core.table_data_collector import MainTableDataCollector
from core.test.util import sample_product_file
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ProductRegistryTestCase(APITestCase):

    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        self.user = User.objects.create_user(
            "john", "john@snow.com", "you_know_nothing"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Get Release previous created by fixtures
        self.release = Release.objects.first()

        # Get Product Types previous created by fixtures
        self.redshift_catalogs = ProductType.objects.get(name="redshift_catalog")
        self.training_set = ProductType.objects.get(name="training_set")

        self.validation_results = ProductType.objects.get(name="validation_results")

    def create_product(self, specz=False, product_type_name=None):
        product_type = self.validation_results.pk
        release = self.release.pk

        if product_type_name == "redshift_catalog" or specz is True:
            product_type = self.redshift_catalogs.pk
            release = None
        elif product_type_name == "training_set":
            product_type = self.training_set.pk

        # Make request
        url = reverse("products-list")
        response = self.client.post(
            url,
            {
                "product_type": product_type,
                "release": release,
                "display_name": "Sample Product",
                "official_product": False,
                "survey": None,
                "pz_code": None,
                "description": "Test product description.",
            },
        )

        data = json.loads(response.content)

        product = Product.objects.get(id=data["id"])
        return product

    def upload_main_file(self, product, extension="csv", compression=None, header=True):

        filename = sample_product_file(extension, compression, header)

        with open(filename, "rb") as fp:
            mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"

            response = self.client.post(
                reverse("product_files-list"),
                dict(
                    {
                        "product": product.pk,
                        "file": fp,
                        "role": 0,
                        "type": mime_type,
                    }
                ),
                format="multipart",
            )
        data = json.loads(response.content)

        return ProductFile.objects.get(pk=data["id"])

    def upload_main_file_from_path(self, product, filepath):
        with open(filepath, "rb") as fp:
            mime_type = mimetypes.guess_type(filepath)[0] or "application/octet-stream"
            response = self.client.post(
                reverse("product_files-list"),
                dict(
                    {
                        "product": product.pk,
                        "file": fp,
                        "role": 0,
                        "type": mime_type,
                    }
                ),
                format="multipart",
            )
        data = json.loads(response.content)
        return ProductFile.objects.get(pk=data["id"])

    def create_multi_file_archive(self, extension="zip"):
        temp_dir = Path(tempfile.mkdtemp(prefix="pz_multi_archive_"))
        file_a = temp_dir / "notes_a.txt"
        file_b = temp_dir / "notes_b.txt"
        file_a.write_text("alpha", encoding="utf-8")
        file_b.write_text("beta", encoding="utf-8")

        if extension == "zip":
            archive_path = temp_dir / "multi.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.write(file_a, arcname=file_a.name)
                archive.write(file_b, arcname=file_b.name)
            return archive_path

        archive_path = temp_dir / "multi.tar"
        with tarfile.open(archive_path, "w") as archive:
            archive.add(file_a, arcname=file_a.name)
            archive.add(file_b, arcname=file_b.name)
        return archive_path

    def create_fake_hats_archive(self, properties_filename="hats.properties"):
        temp_dir = Path(tempfile.mkdtemp(prefix="pz_hats_archive_"))
        hats_root = temp_dir / "mock_hats"
        dataset_dir = hats_root / "dataset" / "Norder=0" / "Npix=0"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        (hats_root / properties_filename).write_text(
            "catalog_name=mock_hats\ndataproduct_type=object\n",
            encoding="utf-8",
        )
        (dataset_dir / "part-0.parquet").write_text("", encoding="utf-8")

        archive_path = temp_dir / "mock_hats.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for file_path in hats_root.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir).as_posix()
                    archive.write(file_path, arcname=arcname)
        return archive_path

    def create_fake_hats_collection_archive(self):
        temp_dir = Path(tempfile.mkdtemp(prefix="pz_hats_collection_archive_"))
        collection_root = temp_dir / "mock_collection"
        catalog_root = collection_root / "catalog"
        catalog_dataset_dir = catalog_root / "dataset" / "Norder=0" / "Npix=0"
        margin_root = collection_root / "margin_10arcs"
        margin_dataset_dir = margin_root / "dataset" / "Norder=0" / "Npix=0"
        catalog_dataset_dir.mkdir(parents=True, exist_ok=True)
        margin_dataset_dir.mkdir(parents=True, exist_ok=True)

        (collection_root / "collection.properties").write_text(
            "collection_name=mock_collection\n",
            encoding="utf-8",
        )
        (catalog_root / "hats.properties").write_text(
            "catalog_name=mock_catalog\ndataproduct_type=object\n",
            encoding="utf-8",
        )
        (margin_root / "hats.properties").write_text(
            "catalog_name=mock_margin\ndataproduct_type=margin\n",
            encoding="utf-8",
        )
        (catalog_dataset_dir / "part-0.parquet").write_text("", encoding="utf-8")
        (margin_dataset_dir / "part-0.parquet").write_text("", encoding="utf-8")

        archive_path = temp_dir / "mock_collection.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for file_path in collection_root.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(temp_dir).as_posix()
                    archive.write(file_path, arcname=arcname)
        return archive_path

    def create_fake_lsdb_module(self, n_rows=12, columns_as_index=False):
        class FakeCatalog:
            columns = pd.Index(["ra", "dec", "z"]) if columns_as_index else ["ra", "dec", "z"]
            all_columns = ["ra", "dec", "z"]

            def __len__(self):
                return n_rows

            def head(self, n=5):
                rows = [
                    {"ra": float(i), "dec": float(i) * -1.0, "z": float(i) * 0.1}
                    for i in range(n_rows)
                ]
                return pd.DataFrame(rows).head(n)

        fake_module = types.ModuleType("lsdb")
        fake_module.open_catalog = mock.Mock(return_value=FakeCatalog())
        return fake_module

    def test_product_registry(self):
        product = self.create_product()
        self.upload_main_file(product, "csv")
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_registry_without_internal_name(self):
        product = self.create_product()
        self.upload_main_file(product, "csv")
        url = reverse("products-registry", kwargs={"pk": product.pk})

        product.internal_name = None
        product.save()
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_registry_compressed_file(self):
        # Cria um novo produto.
        product = self.create_product()
        # Cria um novo Product File Main.
        self.upload_main_file(product, extension="csv", compression="zip", header=True)
        # Url de registro do produto
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        preview_path = Path(
            settings.MEDIA_ROOT, product.path, RegistryProduct.TABLE_PREVIEW_FILENAME
        )
        self.assertTrue(preview_path.exists())

        main_file = ProductFile.objects.get(product=product, role=0)
        self.assertTrue(main_file.name.endswith(".csv"))
        self.assertEqual(main_file.extension, ".csv")
        self.assertFalse(main_file.is_directory)
        self.assertFalse(Path(main_file.file.path).name.endswith(".zip"))

    def test_registry_tgz_file(self):
        product = self.create_product()
        self.upload_main_file(product, extension="csv", compression="tgz", header=True)
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        preview_path = Path(
            settings.MEDIA_ROOT, product.path, RegistryProduct.TABLE_PREVIEW_FILENAME
        )
        self.assertTrue(preview_path.exists())

    def test_registry_rejects_non_hats_multi_file_archive_for_training_set(self):
        product = self.create_product(product_type_name="training_set")
        archive_path = self.create_multi_file_archive(extension="zip")
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 500)
        payload = json.loads(response.content)
        self.assertEqual(
            payload["error"],
            RegistryProduct.NON_HATS_MULTI_FILE_ERROR_MESSAGE,
        )

    def test_registry_rejects_non_hats_multi_file_archive_for_redshift_catalog(self):
        product = self.create_product(product_type_name="redshift_catalog")
        archive_path = self.create_multi_file_archive(extension="tar")
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 500)
        payload = json.loads(response.content)
        self.assertEqual(
            payload["error"],
            RegistryProduct.NON_HATS_MULTI_FILE_ERROR_MESSAGE,
        )

    def test_registry_allows_multi_file_archive_for_validation_results(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_multi_file_archive(extension="zip")
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_registry_replaces_hats_archive_with_directory_main_file(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_fake_hats_archive()
        uploaded_main = self.upload_main_file_from_path(product, archive_path)
        original_archive_path = Path(uploaded_main.file.path)
        url = reverse("products-registry", kwargs={"pk": product.pk})

        with mock.patch.object(
            MainTableDataCollector,
            "_is_hats_with_lsdb",
            autospec=True,
            return_value=True,
        ):
            response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        main_file = ProductFile.objects.get(product=product, role=0)
        extracted_main_path = Path(main_file.file.path)
        self.assertTrue(extracted_main_path.is_dir())
        self.assertTrue(main_file.is_directory)
        self.assertTrue((extracted_main_path / "hats.properties").exists())
        self.assertFalse(original_archive_path.exists())

    def test_registry_replaces_hats_collection_archive_with_collection_directory(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_fake_hats_collection_archive()
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})
        fake_lsdb = self.create_fake_lsdb_module(n_rows=12)

        with mock.patch.dict(sys.modules, {"lsdb": fake_lsdb}):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        main_file = ProductFile.objects.get(product=product, role=0)
        extracted_main_path = Path(main_file.file.path)
        self.assertTrue(main_file.is_directory)
        self.assertTrue((extracted_main_path / "collection.properties").exists())
        self.assertTrue((extracted_main_path / "catalog" / "hats.properties").exists())
        self.assertTrue(
            (extracted_main_path / "margin_10arcs" / "hats.properties").exists()
        )

    def test_registry_uses_lsdb_probe_for_hats_detection(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_fake_hats_archive()
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})

        with mock.patch.object(
            MainTableDataCollector,
            "_is_hats_with_lsdb",
            autospec=True,
            return_value=True,
        ) as lsdb_probe_mock:
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(lsdb_probe_mock.call_count, 1)

    def test_registry_accepts_legacy_hats_properties_filename(self):
        product = self.create_product(product_type_name="training_set")
        archive_path = self.create_fake_hats_archive(properties_filename="properties")
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})
        fake_lsdb = self.create_fake_lsdb_module(n_rows=12)

        with mock.patch.dict(sys.modules, {"lsdb": fake_lsdb}):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        main_file = ProductFile.objects.get(product=product, role=0)
        self.assertTrue(main_file.is_directory)
        self.assertTrue(Path(main_file.file.path).is_dir())

    def test_registry_creates_hats_preview_and_metadata_with_lsdb(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_fake_hats_archive()
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})
        fake_lsdb = self.create_fake_lsdb_module(n_rows=12)

        with mock.patch.dict(sys.modules, {"lsdb": fake_lsdb}):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        preview_path = Path(
            settings.MEDIA_ROOT, product.path, RegistryProduct.TABLE_PREVIEW_FILENAME
        )
        self.assertTrue(preview_path.exists())

        payload = json.loads(preview_path.read_text(encoding="utf-8"))
        self.assertEqual(payload["count"], 10)
        self.assertEqual(payload["columns"], ["ra", "dec", "z"])
        self.assertEqual(len(payload["results"]), 10)

        main_file = ProductFile.objects.get(product=product, role=0)
        self.assertEqual(main_file.n_rows, 12)
        self.assertTrue(main_file.is_directory)
        self.assertTrue(Path(main_file.file.path).is_dir())

    def test_read_data_returns_cached_hats_preview(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_fake_hats_archive()
        self.upload_main_file_from_path(product, archive_path)
        fake_lsdb = self.create_fake_lsdb_module(n_rows=12)

        with mock.patch.dict(sys.modules, {"lsdb": fake_lsdb}):
            self.client.post(reverse("products-registry", kwargs={"pk": product.pk}))

        response = self.client.get(
            reverse("products-read-data", kwargs={"pk": product.pk}),
            {"page": 1, "page_size": 10},
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data["count"], 10)
        self.assertEqual(data["columns"], ["ra", "dec", "z"])
        self.assertEqual(len(data["results"]), 10)

    def test_registry_handles_lsdb_columns_as_pandas_index(self):
        product = self.create_product(product_type_name="validation_results")
        archive_path = self.create_fake_hats_archive()
        self.upload_main_file_from_path(product, archive_path)
        url = reverse("products-registry", kwargs={"pk": product.pk})
        fake_lsdb = self.create_fake_lsdb_module(n_rows=12, columns_as_index=True)

        with mock.patch.dict(sys.modules, {"lsdb": fake_lsdb}):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)

    def test_registry_without_columns(self):

        # Cria um novo produto.
        product = self.create_product()
        # Cria um novo Product File Main.
        self.upload_main_file(product, extension="csv", header=False)
        # Url de registro do produto
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_registry_non_textual_file_keeps_n_rows(self):
        product = self.create_product(specz=True)
        product_file = self.upload_main_file(product, extension="fits")
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        product_file.refresh_from_db()
        self.assertIsNotNone(product_file.n_rows)

    def test_registry_parquet_uses_chunked_path(self):
        product = self.create_product(specz=True)
        product_file = self.upload_main_file(product, extension="pq")
        url = reverse("products-registry", kwargs={"pk": product.pk})

        original_df_from_file = ProductHandle.df_from_file

        def guarded_df_from_file(instance, filepath, **kwargs):
            if str(filepath).lower().endswith((".pq", ".parquet")):
                raise Exception("Parquet should use chunked pyarrow path.")
            return original_df_from_file(instance, filepath, **kwargs)

        with mock.patch.object(
            ProductHandle, "df_from_file", autospec=True, side_effect=guarded_df_from_file
        ):
            response = self.client.post(url)

        self.assertEqual(response.status_code, 200)
        product_file.refresh_from_db()
        self.assertIsNotNone(product_file.n_rows)

    def test_registry_retry(self):
        """Verifica se a função registry pode ser repetida para o mesmo produto/file."""
        # Cria um novo produto.
        product = self.create_product()
        # Cria um novo Product File Main.
        self.upload_main_file(product, extension="csv")
        # Url de registro do produto
        url = reverse("products-registry", kwargs={"pk": product.pk})

        # Try
        response = self.client.post(url)

        # Retry
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

    def test_registry_generates_table_preview_file(self):
        product = self.create_product(specz=True)
        self.upload_main_file(product, extension="csv")
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        preview_path = Path(
            settings.MEDIA_ROOT, product.path, RegistryProduct.TABLE_PREVIEW_FILENAME
        )
        self.assertTrue(preview_path.exists())

        payload = json.loads(preview_path.read_text(encoding="utf-8"))
        self.assertIn("count", payload)
        self.assertIn("columns", payload)
        self.assertIn("results", payload)
        self.assertLessEqual(len(payload["results"]), RegistryProduct.TABLE_PREVIEW_ROWS)

    def test_read_data_uses_cached_table_preview(self):
        product = self.create_product(specz=True)
        self.upload_main_file(product, extension="csv")
        self.client.post(reverse("products-registry", kwargs={"pk": product.pk}))

        with mock.patch(
            "core.views.product.FileHandle.to_df",
            side_effect=Exception("Should not parse file when preview exists."),
        ):
            response = self.client.get(
                reverse("products-read-data", kwargs={"pk": product.pk}),
                {"page": 1, "page_size": 10},
            )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn("results", data)
        self.assertLessEqual(len(data["results"]), RegistryProduct.TABLE_PREVIEW_ROWS)

    def test_read_data_starts_background_preview_when_missing(self):
        product = self.create_product(specz=True)
        self.upload_main_file(product, extension="csv")

        preview_path = RegistryProduct.get_table_preview_path(product)
        processing_path = RegistryProduct.get_table_preview_processing_path(product)
        preview_path.unlink(missing_ok=True)
        processing_path.unlink(missing_ok=True)

        with mock.patch("core.views.product.build_product_table_preview.delay") as delay_mock:
            response = self.client.get(
                reverse("products-read-data", kwargs={"pk": product.pk}),
                {"page": 1, "page_size": 10},
            )

        self.assertEqual(response.status_code, 202)
        data = json.loads(response.content)
        self.assertEqual(
            data["message"],
            "Table preview is being processed in the background.",
        )
        delay_mock.assert_called_once_with(product.pk)
        self.assertTrue(processing_path.exists())

    def test_read_data_does_not_restart_preview_when_already_processing(self):
        product = self.create_product(specz=True)
        self.upload_main_file(product, extension="csv")

        preview_path = RegistryProduct.get_table_preview_path(product)
        processing_path = RegistryProduct.get_table_preview_processing_path(product)
        preview_path.unlink(missing_ok=True)
        processing_path.unlink(missing_ok=True)
        RegistryProduct.start_table_preview_processing(product)

        with mock.patch("core.views.product.build_product_table_preview.delay") as delay_mock:
            response = self.client.get(
                reverse("products-read-data", kwargs={"pk": product.pk}),
                {"page": 1, "page_size": 10},
            )

        self.assertEqual(response.status_code, 202)
        data = json.loads(response.content)
        self.assertEqual(
            data["message"],
            "Table preview is being processed in the background.",
        )
        delay_mock.assert_not_called()

    # def test_registry_redshift_without_header(self):
    #     """Redshift need a file with header"""
    #     # Cria um novo produto.
    #     product = self.create_product()
    #     # Cria um novo Product File Main.
    #     self.upload_main_file(product, extension="csv", header=False)
    #     # Url de registro do produto
    #     url = reverse("products-registry", kwargs={"pk": product.pk})

    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 500)

    # def test_registry_redshift_without_header_compressed(self):
    #     """Redshift need a file with header (compression)"""
    #     # Cria um novo produto.
    #     product = self.create_product()
    #     # Cria um novo Product File Main.
    #     self.upload_main_file(product, extension="csv", compression="zip", header=False)
    #     # Url de registro do produto
    #     url = reverse("products-registry", kwargs={"pk": product.pk})

    #     response = self.client.post(url)
    #     self.assertEqual(response.status_code, 500)
