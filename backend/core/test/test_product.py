import json
import pathlib
import shutil

from core.models import Product, ProductType, Release
from core.serializers import ProductSerializer
from core.views import ProductViewSet
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


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

        self.product_dict = {
            "product_type": self.product_type.pk,
            "release": self.release.pk,
            "display_name": "Sample Product",
            "official_product": False,
            "survey": None,
            "pz_code": None,
            "description": "Test product description.",
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_create_product(self):
        # Make request
        response = self.client.post(self.url, self.product_dict)
        data = json.loads(response.content)

        # Check status response
        self.assertEqual(201, response.status_code)
        # Check database
        self.assertEqual(Product.objects.count(), 1)
        # Check Internal Name
        self.assertEqual(data["internal_name"], f"{ data['id'] }_sample_product")
        # Check User
        self.assertEqual(data["uploaded_by"], self.user.username)
        # Check Product Directory
        relative_path = f"{self.product_type.name}/{data['internal_name']}"
        path = pathlib.Path(settings.MEDIA_ROOT, relative_path)
        self.assertTrue(path.exists())
        # Check Status = 0
        self.assertEqual(data["status"], 0)

    def test_list_product(self):
        # Create a New Product
        response = self.client.post(self.url, self.product_dict)
        product = json.loads(response.content)

        # Make request
        response = self.client.get(self.url)
        # Check status response
        self.assertEqual(200, response.status_code)
        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == Product.objects.count())

        # Check Model to String
        record = Product.objects.get(id=product["id"])
        self.assertEqual(str(record), self.product_dict["display_name"])


class ProductCreateRulesTestCase(APITestCase):
    """Tests the business rules applied to the fields when creating a product."""

    url = reverse("products-list")
    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        # Create a User
        self.user = User.objects.create_user(
            "john", "john@snow.com", "you_know_nothing"
        )
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

        # Get Admin group previous created by fixtures
        self.adm_group = Group.objects.get(name="Admin")

        # Get Release previous created by fixtures
        self.release = Release.objects.first()

        # Get Product Types previous created by fixtures
        self.validation_results = ProductType.objects.get(name="validation_results")

        self.specz_catalogs = ProductType.objects.get(name="specz_catalog")

        self.validation_set = ProductType.objects.get(name="validation_set")

        self.training_set = ProductType.objects.get(name="training_set")

        self.photoz_table = ProductType.objects.get(name="photoz_table")

        self.product_dict = {
            "product_type": self.validation_results.pk,
            "release": None,
            "display_name": "Sample Product",
            "official_product": False,
            "survey": None,
            "pz_code": None,
            "description": "Test product description.",
        }

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_release_field_rules(self):
        """Release must be null in Spec-z Catalog"""
        # Not Allowed Product Type
        product_dict = self.product_dict
        product_dict["release"] = self.release.pk

        # Not Allowed Product Type
        product_dict["product_type"] = self.specz_catalogs.pk
        response = self.client.post(self.url, product_dict)
        data = json.loads(response.content)

        # Check status response
        self.assertEqual(400, response.status_code)

        self.assertTrue("release" in data)

        # Allowed Product Types
        for product_type in [
            self.validation_results.pk,
            self.validation_set.pk,
            self.training_set.pk,
            self.photoz_table.pk,
        ]:
            product_dict["product_type"] = product_type
            response = self.client.post(self.url, product_dict)
            data = json.loads(response.content)

            # Check status response
            self.assertEqual(201, response.status_code)

    def test_survey_field_rules(self):
        """Survey is only allowed in Spec-z Catalog"""

        product_dict = self.product_dict
        product_dict["survey"] = "Test Survey"

        # Not Allowed Product Types
        for product_type in [
            self.validation_results.pk,
            self.validation_set.pk,
            self.training_set.pk,
            self.photoz_table.pk,
        ]:
            product_dict["product_type"] = product_type
            response = self.client.post(self.url, product_dict)
            data = json.loads(response.content)

            # Check status response
            self.assertEqual(400, response.status_code)

            self.assertTrue("survey" in data)

        # Allowed Product Type
        product_dict["product_type"] = self.specz_catalogs.pk
        response = self.client.post(self.url, product_dict)

        # Check status response
        self.assertEqual(201, response.status_code)

    def test_pzcode_field_rules(self):
        """Pzcode is only allowed in Validations Results and Photo-z Table"""

        product_dict = self.product_dict
        product_dict["pz_code"] = "Test PZ Code"

        # Not Allowed Product Types
        for product_type in [
            self.validation_set.pk,
            self.training_set.pk,
            self.specz_catalogs.pk,
        ]:
            product_dict["product_type"] = product_type
            response = self.client.post(self.url, product_dict)
            data = json.loads(response.content)

            # Check status response
            self.assertEqual(400, response.status_code)

            self.assertTrue("pz_code" in data)

        # Allowed Product Types
        for product_type in [
            self.validation_results.pk,
            self.photoz_table.pk,
        ]:
            product_dict["product_type"] = product_type
            response = self.client.post(self.url, product_dict)

            # Check status response
            self.assertEqual(201, response.status_code)

    def test_official_product_by_no_admin_user(self):
        """Official products can only be created by users who are part of the admin group"""
        product_dict = self.product_dict
        product_dict["official_product"] = True
        response = self.client.post(self.url, self.product_dict)
        # Check status response
        self.assertEqual(403, response.status_code)

    def test_official_product_by_admin_user(self):
        """Official products can only be created by users who are part of the admin group"""

        # Create Admin User
        admin_user = User.objects.create_user("newuser", "new@user.com", "newpass")
        admin_user.groups.add(self.adm_group)
        new_token = Token.objects.create(user=admin_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)

        product_dict = self.product_dict
        product_dict["official_product"] = True
        response = self.client.post(self.url, self.product_dict)

        # Check status response
        self.assertEqual(201, response.status_code)


class ProductDetailAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="john", email="john@snow.com", password="you_know_nothing"
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

        self.product_dict = {
            "product_type": self.product_type.pk,
            "release": self.release.pk,
            "display_name": "Sample Product",
            "official_product": False,
            "survey": None,
            "pz_code": None,
            "description": "Test product description.",
        }

        response = self.client.post(reverse("products-list"), self.product_dict)
        data = json.loads(response.content)
        self.product = Product.objects.get(pk=data["id"])

        self.url = reverse("products-detail", kwargs={"pk": self.product.pk})

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_product_object_bundle(self):
        """
        Test to verify object bundle
        """

        # Cria uma requisicao com context user para ser usada no serializer
        factory = APIRequestFactory()
        request = factory.get(self.url)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        request.user = self.user
        serializer_data = ProductSerializer(
            instance=self.product,
            context={"request": request},
        ).data

        # Faz a requisição normalmente e compara o resultado com objeto gerado pelo serializer
        response = self.client.get(self.url)
        response_data = json.loads(response.content)
        self.assertEqual(serializer_data, response_data)

    def test_product_serialized_format(self):
        """Tests if the return json is in the expected format."""
        expected = {
            "id": self.product.pk,
            "release": self.release.pk,
            "release_name": self.release.display_name,
            "product_type": self.product_type.pk,
            "product_type_name": self.product_type.display_name,
            "uploaded_by": self.user.username,
            "is_owner": True,
            "internal_name": self.product.internal_name,
            "display_name": self.product.display_name,
            "official_product": self.product.official_product,
            "survey": self.product.survey,
            "pz_code": self.product.pz_code,
            "description": self.product.description,
            "created_at": self.product.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "status": self.product.status,
        }

        response = self.client.get(self.url)
        response_data = json.loads(response.content)
        self.assertEqual(expected, response_data)

    def test_product_object_delete_authorization(self):
        """Tests if a product can be removed by a user other than the owner"""
        view = ProductViewSet.as_view({"delete": "destroy"})

        new_user = User.objects.create_user("newuser", "new@user.com", "newpass")
        new_token = Token.objects.create(user=new_user)

        # Cria uma requisicao utilizando Factory
        # para que o metodo destroy da view tenha acesso ao request.user
        factory = APIRequestFactory()
        request = factory.delete(self.url, format="json")
        force_authenticate(request, user=new_user, token=new_token)
        request.user = new_user

        raw_response = view(request, pk=self.product.pk)
        response = raw_response.render()

        self.assertEqual(403, response.status_code)

    def test_product_object_delete(self):
        """Tests if the product owner can remove it"""
        view = ProductViewSet.as_view({"delete": "destroy"})

        # Cria uma requisicao utilizando Factory
        # para que o metodo destroy da view tenha acesso ao request.user
        factory = APIRequestFactory()
        request = factory.delete(self.url, format="json")
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        request.user = self.user

        raw_response = view(request, pk=self.product.pk)
        response = raw_response.render()

        self.assertEqual(204, response.status_code)

    def test_access_another_user_product(self):
        """Verifica se é possivel um usuario ler produtos de outro usuario.
        Valida se a flag is_owner retorna False
        """
        # Create a new user
        user = User.objects.create_user("newuser", "new@user.com", "newpass")
        new_token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)

        response = self.client.get(self.url)
        response_data = json.loads(response.content)
        self.assertFalse(response_data["is_owner"])
