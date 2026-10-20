from datetime import timedelta
from unittest.mock import Mock, patch

from core.authentication import JupyterHubAuthentication
from core.models import JupyterHubConsent, TrustedJupyterHub
from core.views.hub_access import HubAccessView
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.test import APIRequestFactory


class ConsentTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="alice")
        self.other = get_user_model().objects.create_user(username="bob")
        self.hub = TrustedJupyterHub.objects.create(
            name="Hub",
            public_url="https://hub.example",
            user_url="https://hub.example/hub/api/user",
            enabled=True,
        )
        app = Application.objects.create(
            name="Web",
            user=self.user,
            client_type="confidential",
            authorization_grant_type="password",
        )
        AccessToken.objects.create(
            user=self.user,
            application=app,
            token="web-token",
            expires=timezone.now() + timedelta(hours=1),
            scope="read write",
        )

    def edit(self, enabled=True, header="Bearer web-token", **extra):
        data = {"enabled": enabled, "signature": self.hub.consent_signature, **extra}
        request = APIRequestFactory().put(
            "/api/hub-access/1/", data, format="json", HTTP_AUTHORIZATION=header
        )
        return HubAccessView.as_view()(request, hub_id=self.hub.pk)

    def authenticate(self):
        response = Mock(status_code=200)
        response.json.return_value = {"kind": "user", "name": "alice"}
        request = APIRequestFactory().get(
            "/api/", HTTP_AUTHORIZATION="JupyterHub https://hub.example secret"
        )
        with patch("core.authentication.requests.get", return_value=response):
            return JupyterHubAuthentication().authenticate(request)

    def test_authorize_authenticate_revoke(self):
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        self.assertEqual(self.edit().status_code, 200)
        self.assertEqual(self.authenticate()[0], self.user)
        self.assertEqual(self.edit(False).status_code, 200)
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        consent = JupyterHubConsent.objects.get()
        self.assertIsNotNone(consent.authorized_at)
        self.assertIsNotNone(consent.revoked_at)

    def test_cannot_authorize_with_hub_personal_token_or_anonymously(self):
        for header in ("JupyterHub https://hub.example secret", "Token personal", ""):
            self.assertIn(self.edit(header=header).status_code, (401, 403))
        self.assertFalse(JupyterHubConsent.objects.exists())

    def test_cannot_choose_another_user(self):
        self.assertEqual(self.edit(user=self.other.pk).status_code, 200)
        self.assertEqual(JupyterHubConsent.objects.get().user, self.user)

    def test_configuration_changes_revoke_even_if_restored(self):
        self.edit()
        old = self.hub.user_url
        self.hub.user_url = "https://hub.example/new/api/user"
        self.hub.save()
        self.hub.user_url = old
        self.hub.save()
        with self.assertRaises(AuthenticationFailed):
            self.authenticate()
        self.assertFalse(JupyterHubConsent.objects.get().enabled)

    def test_stale_form_and_disabled_partner_cannot_be_authorized(self):
        self.assertEqual(self.edit(signature="old").status_code, 400)
        self.hub.enabled = False
        self.hub.save()
        self.assertEqual(self.edit().status_code, 400)
        self.assertFalse(JupyterHubConsent.objects.exists())

    def test_list_contains_only_own_authorization(self):
        JupyterHubConsent.objects.create(
            user=self.other,
            hub=self.hub,
            enabled=True,
            hub_signature=self.hub.consent_signature,
        )
        req = APIRequestFactory().get(
            "/api/hub-access/", HTTP_AUTHORIZATION="Bearer web-token"
        )
        result = HubAccessView.as_view()(req)
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.data[0]["authorized"])

    def test_session_write_requires_csrf(self):
        req = APIRequestFactory(enforce_csrf_checks=True).put(
            "/api/hub-access/1/",
            {"enabled": True, "signature": self.hub.consent_signature},
            format="json",
        )
        req.user = self.user
        self.assertEqual(
            HubAccessView.as_view()(req, hub_id=self.hub.pk).status_code, 403
        )
        self.assertFalse(JupyterHubConsent.objects.exists())

    def test_session_with_valid_csrf_can_authorize(self):
        from django.middleware.csrf import _get_new_csrf_string

        secret = _get_new_csrf_string()
        req = APIRequestFactory(enforce_csrf_checks=True).put(
            "/api/hub-access/1/",
            {"enabled": True, "signature": self.hub.consent_signature},
            format="json",
            HTTP_X_CSRFTOKEN=secret,
        )
        req.user = self.user
        req.COOKIES["csrftoken"] = secret
        self.assertEqual(
            HubAccessView.as_view()(req, hub_id=self.hub.pk).status_code, 200
        )
        self.assertTrue(JupyterHubConsent.objects.get().enabled)

    def test_non_boolean_authorization_is_rejected(self):
        for value in ("true", 1, None):
            self.assertEqual(self.edit(enabled=value).status_code, 400)
        self.assertFalse(JupyterHubConsent.objects.exists())
