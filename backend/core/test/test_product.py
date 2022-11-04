import json

from core.models import ProductType, Release, Product
from core.serializers import ProductSerializer
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
import pathlib
from django.conf import settings
import shutil


class ProductListCreateAPIViewTestCase(APITestCase):
    url = reverse("products-list")

    def setUp(self):
        # Create a Admin User
        self.username = "john"
        self.email = "john@snow.com"
        self.password = "you_know_nothing"
        self.user = User.objects.create_superuser(
            self.username, self.email, self.password
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

        # Create Release
        self.release = Release.objects.create(
            name="lsst_dp0", display_name="LSST DP0", description="LSST Data Preview 0"
        )
        # Create Product Type
        self.product_type = ProductType.objects.create(
            name="validation_results",
            display_name="Validation Results",
            description="Results of a photo-z validation procedure (free format). Usually contains photo-z estimates (single estimates and/or pdf) of a validation set and photo-z validation metrics.",
        )

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_product(self):
        # Prepare data
        product_dict = {
            "product_type": self.product_type.pk,
            "release": self.release.pk,
            "display_name": "Sample Product",
            "official_product": False,
            "survey": None,
            "pz_code": None,
            "description": "Test product description.",
        }
        internal_name = "1_sample_product"

        # Path para o produto
        relative_path = f"{self.product_type.name}/{internal_name}"
        path = pathlib.Path(settings.MEDIA_ROOT, relative_path)
        # Remove o diretório caso exista
        if path.exists():
            shutil.rmtree(path)

        # Make request
        response = self.client.post(self.url, product_dict)
        data = json.loads(response.content)

        # Check status response
        self.assertEqual(201, response.status_code)
        # Check database
        self.assertEqual(Product.objects.count(), 1)
        # Check Internal Name
        self.assertEqual(data["internal_name"], internal_name)
        # Check User
        self.assertEqual(data["uploaded_by"], self.user.username)
        # Check Product Directory
        self.assertTrue(path.exists())
        # Check Status = 0
        self.assertEqual(data["status"], 0)

    def test_list_product(self):
        # Make request
        response = self.client.get(self.url)
        # Check status response
        self.assertEqual(200, response.status_code)
        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == Product.objects.count())


# class ProductDetailAPIViewTestCase(APITestCase):
#     def setUp(self):
#         # Create a Admin User
#         self.username = "john"
#         self.email = "john@snow.com"
#         self.password = "you_know_nothing"
#         self.user = User.objects.create_superuser(
#             self.username, self.email, self.password
#         )
#         self.token = Token.objects.create(user=self.user)
#         self.api_authentication()

#         self.name = "validation_results"
#         self.display_name = "Validation Results"
#         self.description = "Results of a photo-z validation procedure (free format). Usually contains photo-z estimates (single estimates and/or pdf) of a validation set and photo-z validation metrics."
#         self.product = Product.objects.create(
#             name=self.name, display_name=self.display_name, description=self.description
#         )
#         self.url = reverse("products-detail", kwargs={"pk": self.product.pk})

#     def api_authentication(self):
#         self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

#     def test_product_object_bundle(self):
#         """
#         Test to verify object bundle
#         """
#         response = self.client.get(self.url)
#         serializer_data = ProductSerializer(instance=self.product).data
#         response_data = json.loads(response.content)
#         self.assertEqual(serializer_data, response_data)

#     def test_product_object_update_authorization(self):
#         """
#         Test to verify that put call with user not admin
#         """
#         new_user = User.objects.create_user("newuser", "new@user.com", "newpass")
#         new_token = Token.objects.create(user=new_user)
#         self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)

#         # HTTP PUT
#         response = self.client.put(self.url, {"name", "Hacked by new user"})
#         self.assertEqual(403, response.status_code)

#         # HTTP PATCH
#         response = self.client.patch(self.url, {"name", "Hacked by new user"})
#         self.assertEqual(403, response.status_code)

#     def test_product_object_update(self):
#         response = self.client.put(
#             self.url,
#             {
#                 "name": "validation_results_1",
#                 "display_name": "Validation Results 1",
#                 "description": "Validation Results 1",
#             },
#         )
#         # Check status response
#         self.assertEqual(200, response.status_code)

#         # Check database
#         response_data = json.loads(response.content)
#         product = Product.objects.get(id=self.product.id)
#         self.assertEqual(response_data.get("name"), product.name)

#     def test_product_object_partial_update(self):
#         response = self.client.patch(self.url, {"name": "validation_results_1"})

#         # Check status response
#         self.assertEqual(200, response.status_code)

#         # Check database
#         response_data = json.loads(response.content)
#         product = Product.objects.get(id=self.product.id)
#         self.assertEqual(response_data.get("name"), product.name)

#     def test_product_object_delete_authorization(self):
#         """
#         Test to verify that delete call with not admin user
#         """
#         new_user = User.objects.create_user("newuser", "new@user.com", "newpass")
#         new_token = Token.objects.create(user=new_user)
#         self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)
#         response = self.client.delete(self.url)
#         self.assertEqual(403, response.status_code)

#     def test_product_object_delete(self):
#         response = self.client.delete(self.url)
#         self.assertEqual(204, response.status_code)
