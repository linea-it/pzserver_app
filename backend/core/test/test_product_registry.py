import json
import mimetypes

from core.models import Product, ProductFile, ProductType, Release
from core.test.util import sample_product_file
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

        self.validation_results = ProductType.objects.get(name="validation_results")

    def create_product(self, specz=False):

        product_type = self.validation_results.pk
        release = self.release.pk
        if specz == True:
            product_type = self.redshift_catalogs.pk
            release = None

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

            response = self.client.post(
                reverse("product_files-list"),
                dict(
                    {
                        "product": product.pk,
                        "file": fp,
                        "role": 0,
                        "type": mimetypes.guess_type(filename)[0],
                    }
                ),
                format="multipart",
            )
        data = json.loads(response.content)

        return ProductFile.objects.get(pk=data["id"])

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

    def test_registry_without_columns(self):

        # Cria um novo produto.
        product = self.create_product()
        # Cria um novo Product File Main.
        self.upload_main_file(product, extension="csv", header=False)
        # Url de registro do produto
        url = reverse("products-registry", kwargs={"pk": product.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

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
