from pathlib import Path
from tempfile import TemporaryDirectory

from core.models import FileRoles, Product
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase


class SeedLocalDp1SpeczCommandTestCase(TestCase):
    fixtures = ["core/fixtures/initial_data.yaml"]

    def test_command_registers_the_hats_collection_idempotently(self):
        get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="secret",
        )

        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            datasets_dir = temp_path / "datasets"
            upload_dir = temp_path / "uploads"
            source = datasets_dir / "dp1_specz_collection"
            (source / "catalog").mkdir(parents=True)
            (source / "collection.properties").write_text(
                "#HATS Collection\nhats_primary_table_url=catalog\n",
                encoding="utf-8",
            )
            (source / "catalog/hats.properties").write_text(
                "#HATS catalog\nhats_nrows=36145\n",
                encoding="utf-8",
            )

            with self.settings(
                DATASETS_DIR=str(datasets_dir),
                UPLOAD_DIR=str(upload_dir),
            ):
                call_command("seed_local_dp1_specz", username="admin")
                call_command("seed_local_dp1_specz", username="admin")

            product = Product.objects.get(
                internal_name="local_dp1_specz_collection"
            )
            self.assertEqual("dp1", product.release.name)
            self.assertEqual("redshift_catalog", product.product_type.name)
            self.assertTrue(product.official_product)
            self.assertEqual(1, Product.objects.filter(pk=product.pk).count())

            main_file = product.files.get(role=FileRoles.MAIN)
            self.assertTrue(main_file.is_directory)
            self.assertEqual(36145, main_file.n_rows)
            self.assertTrue(
                (
                    upload_dir
                    / product.path
                    / "dp1_specz_collection/collection.properties"
                ).is_file()
            )

            aliases = {
                content.alias: content.column_name
                for content in product.contents.exclude(alias__isnull=True)
            }
            self.assertEqual(
                {
                    "ID": "id",
                    "RA": "ra",
                    "Dec": "dec",
                    "z": "z",
                    "z_flag": "z_flag",
                    "z_err": "z_err",
                    "survey": "survey",
                },
                aliases,
            )
