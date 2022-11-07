import json

from core.models import Release
from core.serializers import ReleaseSerializer
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class ReleaseListCreateAPIViewTestCase(APITestCase):
    url = reverse("releases-list")

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

    def test_create_release(self):
        """Release endpoint is ReadOnly
        only admin users can create new record using admin interface.
        """
        # Prepare data
        release_dict = {
            "name": "lsst_dp0",
            "display_name": "LSST DP0",
            "description": "LSST Data Preview 0",
        }
        # Make request
        response = self.client.post(self.url, release_dict)
        # Check status response
        self.assertEqual(405, response.status_code)
        # Create with Model
        Release.objects.create(
            name=release_dict["name"],
            display_name=release_dict["display_name"],
            description=release_dict["description"],
        )
        # Check database
        self.assertEqual(Release.objects.count(), 1)

    def test_list_release(self):
        # Make request
        response = self.client.get(self.url)
        # Check status response
        self.assertEqual(200, response.status_code)
        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == Release.objects.count())


class ReleaseDetailAPIViewTestCase(APITestCase):
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

        self.name = "lsst_dp0"
        self.display_name = "LSST DP0"
        self.description = "LSST Data Preview 0"
        self.release = Release.objects.create(
            name=self.name, display_name=self.display_name, description=self.description
        )
        self.url = reverse("releases-detail", kwargs={"pk": self.release.pk})

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_release_object_bundle(self):
        """
        Test to verify object bundle
        """
        response = self.client.get(self.url)
        serializer_data = ReleaseSerializer(instance=self.release).data
        response_data = json.loads(response.content)
        self.assertEqual(serializer_data, response_data)

    def test_release_object_update_authorization(self):
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

    def test_release_object_update(self):
        response = self.client.put(
            self.url,
            {
                "name": "lsst_dp1",
                "display_name": "LSST DP1",
                "description": "LSST Data Preview 1",
            },
        )
        # Check status response
        self.assertEqual(405, response.status_code)

    def test_release_object_partial_update(self):
        response = self.client.patch(self.url, {"name": "lsst_dp2"})

        # Check status response
        self.assertEqual(405, response.status_code)

    def test_release_object_delete_authorization(self):
        """
        Test to verify that delete call with not admin user
        """
        new_user = User.objects.create_user("newuser", "new@user.com", "newpass")
        new_token = Token.objects.create(user=new_user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + new_token.key)
        response = self.client.delete(self.url)
        self.assertEqual(405, response.status_code)

    def test_release_object_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(405, response.status_code)
