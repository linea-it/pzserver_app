from core.models import Product, ProductContent, ProductType
from core.process.builders.inputs_builder import InputsBuilder
from django.contrib.auth.models import User
from django.test import TestCase


class InputsBuilderTestCase(TestCase):
    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        self.user = User.objects.create_user(
            "john", "john@snow.com", "you_know_nothing"
        )
        self.product_type = ProductType.objects.get(name="redshift_catalog")
        self.product = Product.objects.create(
            product_type=self.product_type,
            user=self.user,
            display_name="Sample Redshift Catalog",
            official_product=False,
            path="redshift_catalog/sample",
            internal_name="sample_redshift_catalog",
        )

    def test_build_columns_uses_id_alias_from_ucd_mapping(self):
        ProductContent.objects.bulk_create([
            ProductContent(
                product=self.product,
                column_name="object_id",
                ucd="meta.id;meta.main",
                alias="ID",
                order=0,
            ),
            ProductContent(
                product=self.product,
                column_name="RAdeg",
                ucd="pos.eq.ra;meta.main",
                alias="RA",
                order=1,
            ),
            ProductContent(
                product=self.product,
                column_name="DEdeg",
                ucd="pos.eq.dec;meta.main",
                alias="Dec",
                order=2,
            ),
            ProductContent(
                product=self.product,
                column_name="zfinal",
                ucd="src.redshift",
                alias="z",
                order=3,
            ),
        ])

        columns = InputsBuilder(process=None)._build_columns(self.product)

        self.assertEqual(columns["id"], "object_id")
        self.assertEqual(columns["ra"], "RAdeg")
        self.assertEqual(columns["dec"], "DEdeg")
        self.assertEqual(columns["z"], "zfinal")

    def test_build_columns_accepts_id_alias_case_variations(self):
        ProductContent.objects.bulk_create([
            ProductContent(
                product=self.product,
                column_name="object_id",
                ucd="meta.id;meta.main",
                alias="Id",
                order=0,
            ),
            ProductContent(
                product=self.product,
                column_name="RAdeg",
                ucd="pos.eq.ra;meta.main",
                alias="RA",
                order=1,
            ),
            ProductContent(
                product=self.product,
                column_name="DEdeg",
                ucd="pos.eq.dec;meta.main",
                alias="Dec",
                order=2,
            ),
            ProductContent(
                product=self.product,
                column_name="zfinal",
                ucd="src.redshift",
                alias="z",
                order=3,
            ),
        ])

        columns = InputsBuilder(process=None)._build_columns(self.product)

        self.assertEqual(columns["id"], "object_id")

    def test_build_columns_accepts_required_alias_case_variations(self):
        ProductContent.objects.bulk_create([
            ProductContent(
                product=self.product,
                column_name="object_id",
                ucd="meta.id;meta.main",
                alias="ID",
                order=0,
            ),
            ProductContent(
                product=self.product,
                column_name="RAdeg",
                ucd="pos.eq.ra;meta.main",
                alias="ra",
                order=1,
            ),
            ProductContent(
                product=self.product,
                column_name="DEdeg",
                ucd="pos.eq.dec;meta.main",
                alias="DEC",
                order=2,
            ),
            ProductContent(
                product=self.product,
                column_name="zfinal",
                ucd="src.redshift",
                alias="Z",
                order=3,
            ),
        ])

        columns = InputsBuilder(process=None)._build_columns(self.product)

        self.assertEqual(columns["ra"], "RAdeg")
        self.assertEqual(columns["dec"], "DEdeg")
        self.assertEqual(columns["z"], "zfinal")
