import json

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate


class UserTestCase(APITestCase):

    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        # Get Admin group previous created by fixtures
        self.adm_group = Group.objects.get(name="Admin")

    def test_logged_user(self):
        user = User.objects.create_user("john", "john@snow.com", "you_know_nothing")
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("logged_user")

        # Make request
        response = self.client.post(url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        self.assertFalse(data["is_admin"])

    def test_logged_user_admin(self):
        user = User.objects.create_user("john", "john@snow.com", "you_know_nothing")
        user.groups.add(self.adm_group)
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("logged_user")

        # Make request
        response = self.client.post(url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)

        self.assertTrue(data["is_admin"])

    def test_profile_to_str(self):

        # if email display name is email.split('@')
        user = User.objects.create_user("john", "john.snow@got.com", "you_know_nothing")
        self.assertEqual(str(user.profile), user.email.split("@")[0])

        # if email is None display name is username
        user = User.objects.create_user("daenerys", None, "targaryen")
        user.refresh_from_db()
        self.assertEqual(str(user.profile), user.username)


class UserListAPIViewTestCase(APITestCase):

    fixtures = [
        "core/fixtures/initial_data.yaml",
    ]

    def setUp(self):
        # Get Admin group previous created by fixtures
        self.adm_group = Group.objects.get(name="Admin")

    def test_list_users(self):
        # Create a New User
        user = User.objects.create_user("john", "john@snow.com", "you_know_nothing")
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + token.key)

        url = reverse("users-list")

        # Make request
        response = self.client.get(url)
        # Check status response
        self.assertEqual(200, response.status_code)
        # Check database
        data = json.loads(response.content)
        self.assertTrue(len(data["results"]) == User.objects.count())
