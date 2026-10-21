from unittest.mock import Mock, patch

import requests
from core.authentication import HubUnavailable, JupyterHubAuthentication
from core.models import JupyterHubConsent, TrustedJupyterHub
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.test import TestCase
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView


class JupyterHubAuthenticationTests(TestCase):
    def setUp(self):
        caches["jupyterhub"].clear()
        self.addCleanup(caches["jupyterhub"].clear)
        self.user = get_user_model().objects.create_user(username="singulani")
        self.hub = TrustedJupyterHub.objects.create(
            name="LIneA",
            public_url="https://jupyter-dev.linea.org.br",
            user_url="https://jupyter-dev.linea.org.br/hub/api/user",
            enabled=True,
        )
        JupyterHubConsent.objects.create(
            user=self.user,
            hub=self.hub,
            enabled=True,
            hub_signature=self.hub.consent_signature,
        )
        self.http = patch("core.authentication.requests.get").start()
        self.addCleanup(patch.stopall)
        self.response = Mock(status_code=200)
        self.response.json.return_value = {
            "kind": "user",
            "name": "singulani",
            "admin": True,
        }
        self.http.return_value = self.response

    def authenticate(
        self, header="JupyterHub https://jupyter-dev.linea.org.br fake-secret"
    ):
        request = APIRequestFactory().get("/api/", HTTP_AUTHORIZATION=header)
        return JupyterHubAuthentication().authenticate(request)

    def test_verified_identity_maps_to_local_user_without_granting_admin(self):
        user, context = self.authenticate()
        self.assertEqual(user.pk, self.user.pk)
        self.assertFalse(user.is_superuser)
        self.assertNotIn("fake-secret", str(context))
        self.http.assert_called_once_with(
            self.hub.user_url,
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
            "JupyterHub https://jupyter-dev.linea.org.br secret extra",
        ):
            with self.assertRaises(AuthenticationFailed):
                self.authenticate(header)
        self.hub.enabled = False
        self.hub.save()
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
        TrustedJupyterHub.objects.filter(pk=self.hub.pk).update(
            user_url="http://untrusted.example/user"
        )
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

    def test_alias_selects_only_registered_endpoint(self):
        self.hub.aliases = ["https://alias.example/prefix/"]
        self.hub.save()
        JupyterHubConsent.objects.filter(user=self.user, hub=self.hub).update(
            enabled=True, hub_signature=self.hub.consent_signature
        )
        self.authenticate("JupyterHub https://ALIAS.example:443/prefix/ fake-secret")
        self.assertEqual(self.http.call_count, 1)
        self.assertEqual(self.http.call_args.args[0], self.hub.user_url)

    def test_unknown_url_never_sends_token(self):
        with self.assertRaises(AuthenticationFailed):
            self.authenticate("JupyterHub https://unknown.example fake-secret")
        self.http.assert_not_called()

    def test_prefix_is_not_discarded(self):
        with self.assertRaises(AuthenticationFailed):
            self.authenticate(
                "JupyterHub https://jupyter-dev.linea.org.br/other fake-secret"
            )
        self.http.assert_not_called()

    def test_ambiguous_alias_never_sends_token(self):
        other = TrustedJupyterHub.objects.create(
            name="Other",
            public_url="https://other.example",
            user_url="https://other.example/hub/api/user",
            enabled=True,
        )
        # Simulate invalid data inserted outside validated save/admin.
        TrustedJupyterHub.objects.filter(pk=other.pk).update(
            aliases=[self.hub.public_url]
        )
        with self.assertRaises(HubUnavailable):
            self.authenticate()
        self.http.assert_not_called()

    def test_cached_identity_expires_after_five_minutes(self):
        from datetime import timedelta
        from django.utils import timezone

        now = timezone.now()
        with patch("django.core.cache.backends.db.tz_now", return_value=now):
            self.authenticate()
        with patch(
            "django.core.cache.backends.db.tz_now",
            return_value=now + timedelta(seconds=299),
        ):
            self.authenticate()
        self.assertEqual(self.http.call_count, 1)
        with patch(
            "django.core.cache.backends.db.tz_now",
            return_value=now + timedelta(seconds=301),
        ):
            self.authenticate()
        self.assertEqual(self.http.call_count, 2)

    def test_cached_identity_still_requires_local_consent_and_active_user(self):
        self.authenticate()
        JupyterHubConsent.objects.filter(hub=self.hub).update(enabled=False)
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        JupyterHubConsent.objects.filter(hub=self.hub).update(enabled=True)
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        self.assertEqual(self.http.call_count, 1)

    def test_cached_identity_does_not_allow_disabled_hub(self):
        self.authenticate()
        self.hub.enabled = False
        self.hub.save()
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        self.assertEqual(self.http.call_count, 1)

    def test_cache_is_scoped_to_token_and_configuration(self):
        self.authenticate()
        self.authenticate("JupyterHub https://jupyter-dev.linea.org.br another-token")
        self.assertEqual(self.http.call_count, 2)
        self.hub.user_url = "https://jupyter-dev.linea.org.br/new/api/user"
        self.hub.save()
        JupyterHubConsent.objects.filter(hub=self.hub).update(
            enabled=True, hub_signature=self.hub.consent_signature
        )
        self.authenticate()
        self.assertEqual(self.http.call_count, 3)

    def test_cache_contains_no_raw_token_and_hits_do_not_renew_expiry(self):
        cache = caches["jupyterhub"]
        with patch.object(cache, "set", wraps=cache.set) as write:
            self.authenticate()
            self.authenticate()
        write.assert_called_once()
        key, value = write.call_args.args
        self.assertNotIn("fake-secret", key)
        self.assertEqual(value, self.user.username)
        self.assertEqual(write.call_args.kwargs["timeout"], 300)

    def test_failed_validation_is_not_cached(self):
        self.response.status_code = 401
        for _ in range(2):
            with self.assertRaises(AuthenticationFailed):
                self.authenticate()
        self.assertEqual(self.http.call_count, 2)


class AuthenticationChallengeTests(TestCase):
    def response(self, header="", authenticators=None):
        class ProtectedView(APIView):
            permission_classes = [IsAuthenticated]

        request = APIRequestFactory().get("/api/", HTTP_AUTHORIZATION=header)
        return ProtectedView.as_view(
            authentication_classes=authenticators
            or [JupyterHubAuthentication, OAuth2Authentication]
        )(request)

    def test_no_credentials_preserves_existing_oauth_challenge(self):
        previous = self.response(authenticators=[OAuth2Authentication])
        current = self.response()
        self.assertEqual(current.status_code, 401)
        self.assertEqual(current["WWW-Authenticate"], previous["WWW-Authenticate"])
        self.assertEqual(current["WWW-Authenticate"], 'Bearer realm="api"')

    def test_rejected_hub_credential_uses_hub_challenge(self):
        for header in ("JupyterHub unknown fake", "jupyterhub", "JUPYTERHUB"):
            response = self.response(header)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(response["WWW-Authenticate"], "JupyterHub")

    def test_invalid_bearer_preserves_oauth_error_details(self):
        previous = self.response("Bearer invalid", [OAuth2Authentication])
        current = self.response("Bearer invalid")
        self.assertEqual(current.status_code, 401)
        self.assertEqual(current["WWW-Authenticate"], previous["WWW-Authenticate"])
        self.assertTrue(current["WWW-Authenticate"].startswith("Bearer "))
