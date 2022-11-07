import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from core.models import ProductType
from core.serializers import ProductTypeSerializer


class ProductTypeListCreateAPIViewTestCase(APITestCase):
    url = reverse("product_types-list")

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

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_product_type(self):
        """Product Type endpoint is ReadOnly
        only admin users can create new record using admin interface.
        """
        # Prepare data
        product_type_dict = {
            "name": "validation_results",
            "display_name": "Validation Results",
            "description": "Results of a photo-z validation procedure (free format). Usually contains photo-z estimates (single estimates and/or pdf) of a validation set and photo-z validation metrics.",
        }
        # Make request
        response = self.client.post(self.url, product_type_dict)
        # Check status response
        self.assertEqual(405, response.status_code)

        # Create with Model
        record = ProductType.objects.create(
            name=product_type_dict["name"],
            display_name=product_type_dict["display_name"],
            description=product_type_dict["description"],
        )
        # Check database
        self.assertEqual(ProductType.objects.count(), 1)

    def test_list_product_type(self):
        # Make request
        response = self.client.get(self.url)
        # Check status response
        self.assertEqual(200, response.status_code)
        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == ProductType.objects.count())


class ProductTypeDetailAPIViewTestCase(APITestCase):
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

        self.name = "validation_results"
        self.display_name = "Validation Results"
        self.description = "Results of a photo-z validation procedure (free format). Usually contains photo-z estimates (single estimates and/or pdf) of a validation set and photo-z validation metrics."
        self.product_type = ProductType.objects.create(
            name=self.name, display_name=self.display_name, description=self.description
        )
        self.url = reverse("product_types-detail", kwargs={"pk": self.product_type.pk})

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_product_type_object_bundle(self):
        """
        Test to verify object bundle
        """
        response = self.client.get(self.url)
        serializer_data = ProductTypeSerializer(instance=self.product_type).data
        response_data = json.loads(response.content)
        self.assertEqual(serializer_data, response_data)

    def test_product_type_object_update_authorization(self):
        """
        Test to verify that put call with user not admin
        """
        new_user = User.objects.create_user("newuser", "new@user.com", "newpass")
        new_token = Token.objects.create(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)

        # HTTP PUT
        response = self.client.put(self.url, {"name", "Hacked by new user"})
        self.assertEqual(405, response.status_code)

        # HTTP PATCH
        response = self.client.patch(self.url, {"name", "Hacked by new user"})
        self.assertEqual(405, response.status_code)

    def test_product_type_object_update(self):
        response = self.client.put(
            self.url,
            {
                "name": "validation_results_1",
                "display_name": "Validation Results 1",
                "description": "Validation Results 1",
            },
        )
        # Check status response
        self.assertEqual(405, response.status_code)

    def test_product_type_object_partial_update(self):
        response = self.client.patch(self.url, {"name": "validation_results_1"})

        # Check status response
        self.assertEqual(405, response.status_code)

    def test_product_type_object_delete_authorization(self):
        """
        Test to verify that delete call with not admin user
        """
        new_user = User.objects.create_user("newuser", "new@user.com", "newpass")
        new_token = Token.objects.create(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(405, response.status_code)

    def test_product_type_object_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(405, response.status_code)
