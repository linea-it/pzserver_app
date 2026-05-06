import json
import mimetypes
import os
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from core.models import (
    FileRoles,
    FileStorageKind,
    Product,
    ProductFile,
    ProductType,
    Release,
)
from core.serializers import ProductFileSerializer
from core.test.util import sample_product_file
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


class ProductFileListCreateAPIViewTestCase(APITestCase):
    url = reverse("product_files-list")

    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        self.user = User.objects.create_user(
            "john", "john@snow.com", "you_know_nothing"
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

        # Get Release previous created by fixtures
        self.release = Release.objects.first()

        # Get Product Types previous created by fixtures
        self.product_type = ProductType.objects.get(name="validation_results")
        self.training_results = ProductType.objects.get(name="training_results")

        self.product_dict = {
            "product_type": self.product_type.pk,
            "release": self.release.pk,
            "display_name": "Sample Product",
            "official_product": False,
            "survey": None,
            "pz_code": None,
            "description": "Test product description.",
        }

        self.product = self.create_product()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def create_product(self):
        # Make request
        url = reverse("products-list")
        response = self.client.post(url, self.product_dict)
        data = json.loads(response.content)

        product = Product.objects.get(id=data["id"])
        return product

    def create_training_results_product(self):
        url = reverse("products-list")
        response = self.client.post(
            url,
            {
                **self.product_dict,
                "product_type": self.training_results.pk,
            },
        )
        data = json.loads(response.content)
        return Product.objects.get(id=data["id"])

    def test_upload_main_file(self):

        filename = sample_product_file("csv")

        with open(filename) as fp:

            response = self.client.post(
                self.url,
                dict(
                    {
                        "product": self.product.pk,
                        "file": fp,
                        "role": 0,
                        "type": mimetypes.guess_type(filename)[0],
                    }
                ),
                format="multipart",
            )
        data = json.loads(response.content)

        # Check status response
        self.assertEqual(201, response.status_code)

        # Check database
        self.assertEqual(ProductFile.objects.count(), 1)

        # Check if file exists
        pf = ProductFile.objects.get(pk=data["id"])
        self.assertTrue(Path(pf.file.path).exists())

    def test_list_product_file(self):
        # Create a New Product File
        filename = sample_product_file("csv")

        with open(filename) as fp:
            response = self.client.post(
                self.url,
                {
                    "product": self.product.pk,
                    "file": fp,
                    "role": 0,
                    "type": mimetypes.guess_type(filename)[0],
                },
                format="multipart",
            )
            product_file = json.loads(response.content)

        # Make request
        response = self.client.get(self.url)
        # Check status response
        self.assertEqual(200, response.status_code)
        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == ProductFile.objects.count())

        # Check Model to String
        record = ProductFile.objects.get(id=product_file["id"])
        self.assertTrue(str(record).startswith(self.product.display_name))

    @patch("core.views.product_file.validate_and_store_hats_archive")
    def test_upload_hats_main_file(self, validate_and_store):
        validate_and_store.return_value = (
            f"{self.product.path}/main",
            {
                "columns": ["ra", "dec", "z"],
                "dtypes": {"ra": "float64", "dec": "float64", "z": "float64"},
                "npartitions": 1,
                "n_rows": 3,
            },
        )
        archive = BytesIO(b"fake hats archive")
        archive.name = "catalog.tar.gz"

        response = self.client.post(
            self.url,
            {
                "product": self.product.pk,
                "file": archive,
                "role": 0,
                "type": "application/gzip",
            },
            format="multipart",
        )

        data = json.loads(response.content)
        self.assertEqual(201, response.status_code)
        product_file = ProductFile.objects.get(pk=data["id"])
        self.assertEqual(product_file.storage_kind, FileStorageKind.HATS_COLLECTION)
        self.assertEqual(product_file.file.name, f"{self.product.path}/main")
        self.assertEqual(product_file.metadata["columns"], ["ra", "dec", "z"])
        self.assertEqual(product_file.n_rows, 3)

    @patch("core.views.product_file.validate_hats_archive")
    def test_training_results_rejects_hats_main_file(self, validate_hats):
        product = self.create_training_results_product()
        validate_hats.return_value = {"columns": ["ra", "dec"]}
        archive = BytesIO(b"fake hats archive")
        archive.name = "catalog.tar.gz"

        response = self.client.post(
            self.url,
            {
                "product": product.pk,
                "file": archive,
                "role": 0,
                "type": "application/gzip",
            },
            format="multipart",
        )

        data = json.loads(response.content)
        self.assertEqual(400, response.status_code)
        self.assertIn("HATS collections are not accepted", data["error"])


class ProductFileDetailAPIViewTestCase(APITestCase):

    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        # Create a user and Autenticate
        self.user = User.objects.create_user(
            username="john", email="john@snow.com", password="you_know_nothing"
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        # Get Release previous created by fixtures
        self.release = Release.objects.first()

        # Get Product Types previous created by fixtures
        self.product_type = ProductType.objects.get(name="validation_results")

        # Create a Product
        response = self.client.post(
            reverse("products-list"),
            {
                "product_type": self.product_type.pk,
                "release": self.release.pk,
                "display_name": "Sample Product",
                "official_product": False,
                "survey": None,
                "pz_code": None,
                "description": "Test product description.",
            },
        )
        data = json.loads(response.content)
        self.product = Product.objects.get(pk=data["id"])

        # Upload a Product File.
        # Create a New Product File
        filename = sample_product_file("csv")

        with open(filename) as fp:
            response = self.client.post(
                reverse("product_files-list"),
                {
                    "product": self.product.pk,
                    "file": fp,
                    "role": 0,
                    "type": mimetypes.guess_type(filename)[0],
                },
                format="multipart",
            )
        product_file = json.loads(response.content)

        # Check Model to String
        self.product_file = ProductFile.objects.get(id=product_file["id"])

        self.url = reverse("product_files-detail", kwargs={"pk": self.product_file.pk})

    def test_product_file_object_bundle(self):
        """
        Test to verify object bundle
        """

        # Cria uma requisicao com context user para ser usada no serializer
        factory = APIRequestFactory()
        request = factory.get(self.url)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        request.user = self.user
        serializer_data = ProductFileSerializer(
            instance=self.product_file,
            context={"request": request},
        ).data

        # Faz a requisição normalmente e compara o resultado com objeto gerado pelo serializer
        response = self.client.get(self.url)
        response_data = json.loads(response.content)
        self.assertEqual(serializer_data, response_data)

    def test_product_file_serialized_format(self):
        """Tests if the return json is in the expected format."""

        # Cria uma requisicao com context user para ser usada no serializer
        factory = APIRequestFactory()
        request = factory.get(self.url)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        request.user = self.user
        serializer_data = ProductFileSerializer(
            instance=self.product_file,
            context={"request": request},
        ).data

        expected = {
            "id": self.product_file.pk,
            "product": self.product.pk,
            "file": serializer_data["file"],
            "role": self.product_file.role,
            "role_name": serializer_data["role_name"],
            "name": self.product_file.name,
            "type": mimetypes.guess_type(os.path.basename(self.product_file.file.name))[
                0
            ],
            "size": self.product_file.file.size,
            "n_rows": None,
            "extension": os.path.splitext(self.product_file.file.name)[1],
            "storage_kind": FileStorageKind.FILE,
            "metadata": {},
            "created": self.product_file.created.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "updated": self.product_file.updated.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "can_delete": True,
        }

        response = self.client.get(self.url)
        response_data = json.loads(response.content)

        self.assertEqual(response_data, expected)

    def test_product_file_update(self):
        """
        Test to verify if update is Not avalialble
        """
        # HTTP PUT
        response = self.client.put(self.url, {"name", "Updated File Name"})
        self.assertEqual(response.status_code, 405)

        # HTTP PATCH
        response = self.client.patch(self.url, {"name", "Updated File Name"})
        self.assertEqual(response.status_code, 405)

    def test_product_file_delete(self):
        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, 204)
