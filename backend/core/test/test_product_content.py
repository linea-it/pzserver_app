import json

from core.models import Product, ProductContent, ProductType, Release
from core.serializers import ProductContentSerializer
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


class ProductContentListCreateAPIViewTestCase(APITestCase):
    url = reverse("product_contents-list")

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
        self.product_type = ProductType.objects.get(name="validation_results")

        self.product = self.create_product()

        self.content_dict = {
            "product": self.product.pk,
            "column_name": "ra",
            "ucd": "pos.eq.ra;meta.main",
            "order": 0,
        }

    def create_product(self):
        # Make request
        url = reverse("products-list")
        response = self.client.post(
            url,
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

        product = Product.objects.get(id=data["id"])
        return product

    def test_create_product_content(self):
        # Make request
        response = self.client.post(self.url, self.content_dict)
        data = json.loads(response.content)

        # Check status response
        self.assertEqual(response.status_code, 201)

        # Check Database
        self.assertEqual(
            ProductContent.objects.filter(product_id=self.product.pk).count(), 1
        )

    def test_list_product_content(self):
        # Create a ProductContent
        response = self.client.post(self.url, self.content_dict)
        pcontent = json.loads(response.content)

        # Make request
        response = self.client.get(self.url)
        # Check status response
        self.assertEqual(200, response.status_code)

        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == ProductContent.objects.count())

        # Check Model to String
        record = ProductContent.objects.get(id=pcontent["id"])
        self.assertEqual(
            str(record), f"{self.product.display_name} - {pcontent['column_name']}"
        )

    def test_list_product_content_filter_by_product(self):
        # Create a ProductContent
        response = self.client.post(self.url, self.content_dict)
        pcontent = json.loads(response.content)

        url = reverse("product_contents-list")
        # Make request
        response = self.client.get(url, {"product": self.product.pk})
        
        # Check status response
        self.assertEqual(200, response.status_code)

        # Check database
        data = json.loads(response.content)
        self.assertEqual(
            len(data["results"]),
            ProductContent.objects.filter(product_id=self.product.pk).count(),
        )


class ProductContentDetailAPIViewTestCase(APITestCase):
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
        self.product_type = ProductType.objects.get(name="validation_results")

        self.product = self.create_product()

        self.content_dict = {
            "product": self.product.pk,
            "column_name": "ra",
            "ucd": "pos.eq.ra;meta.main",
            "alias": "RA",
            "order": 0,
        }

    def create_product(self):
        # Make request
        url = reverse("products-list")
        response = self.client.post(
            url,
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

        product = Product.objects.get(id=data["id"])
        return product

    def create_product_content(self):
        # Make request
        url = reverse("product_contents-list")
        response = self.client.post(url, self.content_dict)
        data = json.loads(response.content)

        pdcontent = ProductContent.objects.get(id=data["id"])
        return pdcontent

    def test_product_content_object_bundle(self):
        """
        Test to verify object bundle
        """
        pdcontent = self.create_product_content()

        url = reverse("product_contents-detail", kwargs={"pk": pdcontent.pk})

        # Cria uma requisicao com context user para ser usada no serializer
        factory = APIRequestFactory()
        request = factory.get(url)
        force_authenticate(request, user=self.user, token=self.user.auth_token)
        request.user = self.user
        serializer_data = ProductContentSerializer(
            instance=pdcontent,
            context={"request": request},
        ).data

        # Faz a requisição normalmente e compara o resultado com objeto gerado pelo serializer
        response = self.client.get(url)
        response_data = json.loads(response.content)
        self.assertEqual(serializer_data, response_data)

    def test_product_serialized_format(self):
        """Tests if the return json is in the expected format."""

        pdcontent = self.create_product_content()

        url = reverse("product_contents-detail", kwargs={"pk": pdcontent.pk})

        expected = {
            "id": pdcontent.pk,
            "product": self.product.pk,
            "column_name": self.content_dict["column_name"],
            "ucd": self.content_dict["ucd"],
            "alias": self.content_dict["alias"],
            "order": self.content_dict["order"],
        }

        response = self.client.get(url)
        response_data = json.loads(response.content)
        self.assertEqual(response_data, expected)

    def test_product_content_object_update(self):
        pdcontent = self.create_product_content()

        url = reverse("product_contents-detail", kwargs={"pk": pdcontent.pk})

        response = self.client.put(
            url,
            {
                "product": self.product.pk,
                "column_name": "updated_column_name",
                "ucd": "updated_ucd",
                "order": 1,
            },
        )
        # Check status response
        self.assertEqual(response.status_code, 200)

    def test_product_content_patch_update(self):
        pdcontent = self.create_product_content()

        url = reverse("product_contents-detail", kwargs={"pk": pdcontent.pk})

        response = self.client.patch(
            url,
            {
                "ucd": "updated_ucd",
                "order": 1,
            },
        )
        # Check status response
        self.assertEqual(response.status_code, 200)

    def test_product_content_delete(self):
        pdcontent = self.create_product_content()

        url = reverse("product_contents-detail", kwargs={"pk": pdcontent.pk})

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
