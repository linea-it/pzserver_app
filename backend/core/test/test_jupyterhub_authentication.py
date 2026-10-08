from unittest.mock import Mock, patch

import requests
from core.authentication import HubUnavailable, JupyterHubAuthentication
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory


class JupyterHubAuthenticationTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="singulani")
        self.partners = {
            "linea-dev": {
                "enabled": True,
                "user_url": "https://jupyter-dev.linea.org.br/hub/api/user",
            }
        }
        self.config = override_settings(JUPYTERHUB_PARTNERS=self.partners)
        self.config.enable()
        self.addCleanup(self.config.disable)
        self.http = patch("core.authentication.requests.get").start()
        self.addCleanup(patch.stopall)
        self.response = Mock(status_code=200)
        self.response.json.return_value = {
            "kind": "user",
            "name": "singulani",
            "admin": True,
        }
        self.http.return_value = self.response

    def authenticate(self, header="JupyterHub linea-dev fake-secret"):
        request = APIRequestFactory().get("/api/", HTTP_AUTHORIZATION=header)
        return JupyterHubAuthentication().authenticate(request)

    def test_verified_identity_maps_to_local_user_without_granting_admin(self):
        user, context = self.authenticate()
        self.assertEqual(user.pk, self.user.pk)
        self.assertFalse(user.is_superuser)
        self.assertNotIn("fake-secret", str(context))
        self.http.assert_called_once_with(
            self.partners["linea-dev"]["user_url"],
            headers={"Authorization": "token fake-secret"},
            timeout=(5, 10),
            allow_redirects=False,
        )

    def test_other_authentication_schemes_are_untouched(self):
        for header in ("", "Token old-token", "Bearer oauth-token"):
            self.assertIsNone(self.authenticate(header))
        self.http.assert_not_called()

    def test_unknown_disabled_and_malformed_requests_never_contact_hub(self):
        for header in (
            "JupyterHub unknown secret",
            "JupyterHub",
            "JupyterHub linea-dev secret extra",
        ):
            with self.assertRaises(AuthenticationFailed):
                self.authenticate(header)
        self.partners["linea-dev"]["enabled"] = False
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        self.http.assert_not_called()

    def test_invalid_token_is_rejected(self):
        for status in (401, 403):
            self.response.status_code = status
            with self.assertRaises(AuthenticationFailed):
                self.authenticate()

    def test_redirects_server_errors_and_invalid_json_fail_closed(self):
        for status in (302, 404, 500):
            self.response.status_code = status
            with self.assertRaises(HubUnavailable):
                self.authenticate()
        self.response.status_code = 200
        self.response.json.side_effect = ValueError()
        with self.assertRaises(HubUnavailable):
            self.authenticate()

    def test_network_failure_does_not_expose_exception_details(self):
        self.http.side_effect = requests.Timeout("fake-secret")
        with self.assertRaises(HubUnavailable) as error:
            self.authenticate()
        self.assertNotIn("fake-secret", str(error.exception))

    def test_unknown_service_and_malformed_identities_are_rejected(self):
        for identity in (
            {"kind": "user", "name": "unknown"},
            {"kind": "service", "name": "singulani"},
            {"kind": "user", "name": []},
            [],
        ):
            self.response.json.return_value = identity
            with self.assertRaises(AuthenticationFailed):
                self.authenticate()

    def test_inactive_local_account_is_rejected(self):
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()

    def test_insecure_endpoint_is_not_contacted(self):
        self.partners["linea-dev"]["user_url"] = "http://untrusted.example/user"
        with self.assertRaises(HubUnavailable):
            self.authenticate()
        self.http.assert_not_called()

    def test_username_must_match_exactly_without_creating_accounts(self):
        count = get_user_model().objects.count()
        for name in ("Singulani", " singulani", "singulani ", "another-user"):
            self.response.json.return_value = {"kind": "user", "name": name}
            with self.assertRaises(AuthenticationFailed):
                self.authenticate()
        self.assertEqual(get_user_model().objects.count(), count)

    def test_database_collation_cannot_relax_exact_match(self):
        self.response.json.return_value = {"kind": "user", "name": "SINGULANI"}
        with patch(
            "django.contrib.auth.models.User.objects.get", return_value=self.user
        ):
            with self.assertRaises(AuthenticationFailed):
                self.authenticate()

    def test_legacy_mapping_cannot_authenticate_a_different_username(self):
        self.partners["linea-dev"]["users"] = {"other": self.user.pk}
        self.response.json.return_value = {"kind": "user", "name": "other"}
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
