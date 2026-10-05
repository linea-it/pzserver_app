from unittest import mock

import requests
from core.maestro import Maestro
from core.models import Release
from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase


class MaestroHatsConfigTestCase(APITestCase):
    @mock.patch("core.maestro.MaestroApi")
    def test_requests_release_hats_config_from_orchestration(self, api_class):
        api_class.return_value.get_request.return_value = {
            "success": True,
            "data": {"release": "dp1", "config": {}},
        }

        result = Maestro("http://orchestrator").hats_config("dp1")

        api_class.return_value.get_request.assert_called_once_with(
            "http://orchestrator/api/releases/hats_config/",
            params={"release": "dp1"},
        )
        self.assertEqual("dp1", result["release"])


@override_settings(ORCHEST_URL="http://orchestrator")
class ReleaseHatsConfigAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="hats-user",
            password="test-password",
        )
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        self.release = Release.objects.create(
            name="dp1",
            display_name="LSST DP1",
            indexing_column="objectId",
            is_public=True,
        )
        self.url = reverse(
            "releases-hats-config",
            kwargs={"pk": self.release.pk},
        )

    @mock.patch("core.views.release.Maestro")
    def test_returns_sanitized_orchestration_config(self, maestro_class):
        maestro_class.return_value.hats_config.return_value = {
            "release": "dp1",
            "last_modified": "2026-09-21T12:00:00Z",
            "config": {
                "input": {
                    "catalog_folder": "/datasets/dp1/catalogs",
                    "which_release": "LSST_DP1",
                    "compute_magnitude": True,
                    "compute_dereddening": True,
                },
                "output": {
                    "base_path": "/processes/science_catalogs",
                    "save_as": "hats",
                },
                "cluster": {"executor": "slurm"},
                "dust": {
                    "path_to_dustmaps": "/datasets/dustmaps",
                    "use_dustmap": "sfd",
                },
            },
        }

        response = self.client.get(self.url)

        self.assertEqual(200, response.status_code)
        maestro_class.assert_called_once_with(url="http://orchestrator")
        maestro_class.return_value.hats_config.assert_called_once_with("dp1")
        self.assertEqual("dp1", response.data["release"])
        self.assertEqual(
            {
                "input": {
                    "compute_magnitude": True,
                    "compute_dereddening": True,
                },
                "output": {"save_as": "hats"},
                "dust": {"use_dustmap": "sfd"},
            },
            response.data["config"],
        )

    @mock.patch("core.views.release.Maestro")
    def test_returns_bad_gateway_when_orchestration_is_unavailable(
        self,
        maestro_class,
    ):
        maestro_class.return_value.hats_config.side_effect = (
            requests.exceptions.ConnectionError("unavailable")
        )

        response = self.client.get(self.url)

        self.assertEqual(502, response.status_code)
        self.assertEqual(
            "Could not retrieve the release HATS configuration.",
            response.data["error"],
        )

    @mock.patch("core.views.release.Maestro")
    def test_returns_bad_gateway_for_invalid_orchestration_response(
        self,
        maestro_class,
    ):
        maestro_class.return_value.hats_config.return_value = {
            "release": "dp1",
            "last_modified": "2026-09-21T12:00:00Z",
            "config": [],
        }

        response = self.client.get(self.url)

        self.assertEqual(502, response.status_code)

    @mock.patch("core.views.release.Maestro")
    def test_returns_bad_gateway_for_invalid_upstream_metadata(self, maestro_class):
        maestro_class.return_value.hats_config.return_value = {
            "release": "dp1",
            "last_modified": "not-a-date",
            "config": {"dust": {"use_dustmap": "sfd"}},
        }

        response = self.client.get(self.url)

        self.assertEqual(502, response.status_code)

    @mock.patch("core.views.release.Maestro")
    def test_does_not_fetch_config_for_inaccessible_release(self, maestro_class):
        private_group = Group.objects.create(name="private-release")
        self.release.is_public = False
        self.release.save(update_fields=["is_public"])
        self.release.access_groups.add(private_group)

        response = self.client.get(self.url)

        self.assertEqual(404, response.status_code)
        maestro_class.assert_not_called()
