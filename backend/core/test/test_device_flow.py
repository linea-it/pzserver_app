"""Device Flow regressions using real OAuth views and database."""

from datetime import timedelta
from unittest import skipUnless
from urllib.parse import urlencode

from django.contrib.auth import get_user_model
from django.test import (
    Client,
    TestCase,
    TransactionTestCase,
    override_settings,
    skipUnlessDBFeature,
)
from django.urls import include, path
from core.views.device_access import DeviceAccessView
from django.utils import timezone
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import Application
from oauth2_provider import models as oauth_models

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

DeviceGrant = getattr(oauth_models, "DeviceGrant", None)
if DeviceGrant is not None:
    from core.views.device_oauth import WebTokenView


class ProtectedView(APIView):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"username": request.user.username})


urlpatterns = (
    [
        path("api/device-oauth/", include("core.device_oauth_urls")),
        path("protected/", ProtectedView.as_view()),
        path("api/device-access/", DeviceAccessView.as_view()),
        path("api/device-access/<uuid:access_id>/", DeviceAccessView.as_view()),
        path("api/auth/token", WebTokenView.as_view()),
        path("api/auth/token/", WebTokenView.as_view()),
        path("api/auth/", include("drf_social_oauth2.urls", namespace="drf")),
    ]
    if DeviceGrant is not None
    else []
)


@skipUnless(DeviceGrant is not None, "Requires Django OAuth Toolkit 3.4.1")
@override_settings(
    ROOT_URLCONF=__name__,
    OAUTH2_PROVIDER={
        "OAUTH_DEVICE_VERIFICATION_URI": "https://testserver/api/device-oauth/device/",
        "ACCESS_TOKEN_EXPIRE_SECONDS": 600,
        "ALWAYS_RELOAD_OAUTHLIB_CORE": True,
    },
)
class DeviceFlowTests(TestCase):
    base = "/api/device-oauth/"

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="alice", password="test-password"
        )
        self.app = Application.objects.create(
            name="Python test client",
            client_id="python-test",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_DEVICE_CODE,
        )
        self.browser = Client(enforce_csrf_checks=True)

    def post(self, url, data):
        return self.client.post(
            url, urlencode(data), content_type="application/x-www-form-urlencoded"
        )

    def start(self):
        response = self.post(
            self.base + "device-authorization/",
            {"client_id": self.app.client_id, "scope": "read write"},
        )
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def poll(self, device):
        return self.post(
            self.base + "token/",
            {
                "client_id": self.app.client_id,
                "device_code": device["device_code"],
                "grant_type": Application.GRANT_DEVICE_CODE,
            },
        )

    def approve(self, device, action="accept"):
        from django.conf import settings

        self.browser.force_login(self.user)
        page = self.browser.get(device["verification_uri"])
        self.assertEqual(page.status_code, 200)
        csrf = self.browser.cookies[settings.CSRF_COOKIE_NAME].value
        response = self.browser.post(
            device["verification_uri"],
            {"user_code": device["user_code"], "csrfmiddlewaretoken": csrf},
        )
        self.assertEqual(response.status_code, 302, response.content)
        confirmation = response.url
        self.assertEqual(self.browser.get(confirmation).status_code, 200)
        # CSRF is enforced on the actual browser approval endpoint.
        self.assertEqual(
            self.browser.post(confirmation, {"action": action}).status_code, 403
        )
        result = self.browser.post(
            confirmation, {"action": action, "csrfmiddlewaretoken": csrf}
        )
        self.assertEqual(result.status_code, 302, result.content)

    def test_oauthlib_4_scope_in_device_response_is_accepted(self):
        from unittest.mock import patch

        from core.views.device_oauth import DeviceAuthorizationView

        payload = {
            "verification_uri": "https://testserver/api/device-oauth/device/",
            "verification_uri_complete": None,
            "expires_in": 600,
            "user_code": "SCOPE123",
            "device_code": "private-scope-device-code",
            "interval": 5,
            "scope": "read write",
        }
        with patch.object(
            DeviceAuthorizationView,
            "create_device_authorization_response",
            return_value=({}, payload, 200),
        ):
            response = self.post(
                self.base + "device-authorization/",
                {"client_id": self.app.client_id, "scope": "read write"},
            )

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(
            DeviceGrant.objects.get(device_code=payload["device_code"]).scope,
            "read write",
        )

    @override_settings(OAUTH2_PROVIDER={"ALWAYS_RELOAD_OAUTHLIB_CORE": False})
    def test_legacy_parent_cache_cannot_replace_device_validator(self):
        from unittest.mock import patch
        from drf_social_oauth2.views import TokenView as SocialTokenView
        from core.views.device_oauth import DeviceLifetimeValidator, WebTokenView

        class FreshWebTokenView(WebTokenView):
            pass

        with patch.object(SocialTokenView, "_oauthlib_core", object(), create=True):
            core = FreshWebTokenView.get_oauthlib_core()
            self.assertIsInstance(
                core.server.request_validator, DeviceLifetimeValidator
            )
            self.assertIs(core, FreshWebTokenView.get_oauthlib_core())

    def test_device_lifetimes_rotation_and_idle_expiration(self):
        from oauth2_provider.models import RefreshToken

        device = self.start()
        self.approve(device)
        tokens = self.poll(device).json()
        self.assertEqual(tokens["expires_in"], 3600)
        refreshed = self.post(
            self.base + "token/",
            {
                "client_id": self.app.client_id,
                "grant_type": "refresh_token",
                "refresh_token": tokens["refresh_token"],
            },
        )
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        self.assertNotEqual(refreshed.json()["refresh_token"], tokens["refresh_token"])
        RefreshToken.objects.filter(application=self.app, revoked__isnull=True).update(
            created=timezone.now() - timedelta(days=30, seconds=1)
        )
        for endpoint in (self.base + "token/", "/api/auth/token"):
            response = self.post(
                endpoint,
                {
                    "client_id": self.app.client_id,
                    "grant_type": "refresh_token",
                    "refresh_token": refreshed.json()["refresh_token"],
                },
            )
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()["error"], "invalid_grant")

    def test_connected_access_rotation_revoke_and_ownership(self):
        from core.models import DeviceAccess
        from oauth2_provider.models import RefreshToken
        from rest_framework.test import APIClient

        def issue():
            device = self.start()
            self.approve(device)
            return self.poll(device).json()

        first = issue()
        second = issue()
        access = DeviceAccess.objects.get(
            token_family=RefreshToken.objects.get(
                token=first["refresh_token"]
            ).token_family
        )
        old_id = access.pk
        renewed = self.post(
            self.base + "token/",
            {
                "client_id": self.app.client_id,
                "grant_type": "refresh_token",
                "refresh_token": first["refresh_token"],
            },
        )
        self.assertEqual(renewed.status_code, 200)
        access.refresh_from_db()
        self.assertIsNotNone(access.last_renewed_at)
        self.assertEqual(DeviceAccess.objects.count(), 2)
        browser = APIClient()
        browser.force_login(self.user)
        listing = browser.get("/api/device-access/")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.data), 2)
        for secret in (*first.values(), *second.values()):
            if isinstance(secret, str) and len(secret) > 20:
                self.assertNotIn(secret, listing.content.decode())
        endpoint = f"/api/device-access/{old_id}/"
        stranger = get_user_model().objects.create_user(username="stranger")
        other = APIClient()
        other.force_login(stranger)
        self.assertEqual(other.get("/api/device-access/").data, [])
        self.assertEqual(other.delete(endpoint).status_code, 404)
        self.assertEqual(other.patch(endpoint, {"name": "stolen"}).status_code, 404)
        self.assertEqual(
            browser.patch(endpoint, {"name": "Local notebook"}).status_code, 200
        )
        self.assertEqual(browser.delete(endpoint).status_code, 204)
        self.assertEqual(browser.delete(endpoint).status_code, 204)
        access.refresh_from_db()
        self.assertIsNotNone(access.revoked_at)
        for tokens in (first, renewed.json()):
            self.assertIn(
                self.client.get(
                    "/protected/", HTTP_AUTHORIZATION="Bearer " + tokens["access_token"]
                ).status_code,
                (401, 403),
            )
            result = self.post(
                "/api/auth/token",
                {
                    "client_id": self.app.client_id,
                    "grant_type": "refresh_token",
                    "refresh_token": tokens["refresh_token"],
                },
            )
            self.assertEqual(result.json()["error"], "invalid_grant")
        self.assertEqual(
            self.client.get(
                "/protected/", HTTP_AUTHORIZATION="Bearer " + second["access_token"]
            ).status_code,
            200,
        )
        self.assertEqual(browser.get("/api/device-access/").status_code, 200)

    def test_management_requires_web_login_and_session_csrf(self):
        from core.models import DeviceAccess
        from django.conf import settings
        from rest_framework.test import APIClient

        device = self.start()
        self.approve(device)
        tokens = self.poll(device).json()
        endpoint = f"/api/device-access/{DeviceAccess.objects.get().pk}/"
        api = APIClient()
        self.assertIn(api.get("/api/device-access/").status_code, (401, 403))
        self.assertEqual(
            api.get(
                "/api/device-access/",
                HTTP_AUTHORIZATION="Bearer " + tokens["access_token"],
            ).status_code,
            403,
        )
        self.assertEqual(
            api.delete(endpoint, HTTP_AUTHORIZATION="Token manual").status_code, 403
        )
        csrf = self.browser.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(self.browser.delete(endpoint).status_code, 403)
        self.assertEqual(
            self.browser.delete(endpoint, HTTP_X_CSRFTOKEN=csrf).status_code, 204
        )

    def test_web_oauth_can_manage_and_bad_names_are_rejected(self):
        from core.models import DeviceAccess
        from oauth2_provider.models import AccessToken
        from rest_framework.test import APIClient

        device = self.start()
        self.approve(device)
        self.poll(device)
        web = Application.objects.create(
            client_id="web", authorization_grant_type=Application.GRANT_PASSWORD
        )
        token = AccessToken.objects.create(
            user=self.user,
            application=web,
            token="web-token",
            scope="read write",
            expires=timezone.now() + timedelta(hours=1),
        )
        api = APIClient()
        api.credentials(HTTP_AUTHORIZATION="Bearer " + token.token)
        with override_settings(PZSERVER_WEB_CLIENT_ID="web"):
            self.assertEqual(api.get("/api/device-access/").status_code, 200)
            for name in ("", "x" * 101, "bad\nname", None):
                response = api.patch(
                    f"/api/device-access/{DeviceAccess.objects.get().pk}/",
                    {"name": name},
                    format="json",
                )
                self.assertEqual(response.status_code, 400)

    def test_existing_device_families_are_imported_without_web_tokens(self):
        import importlib
        import uuid
        from types import SimpleNamespace
        from django.apps import apps
        from django.db import connection
        from core.models import DeviceAccess
        from oauth2_provider.models import RefreshToken

        family = uuid.uuid4()
        for index in range(2):
            RefreshToken.objects.create(
                user=self.user,
                application=self.app,
                token=f"old-refresh-{index}",
                token_family=family,
            )
        web = Application.objects.create(
            client_id="old-web", authorization_grant_type=Application.GRANT_PASSWORD
        )
        RefreshToken.objects.create(
            user=self.user,
            application=web,
            token="web-refresh",
            token_family=uuid.uuid4(),
        )
        migrate = importlib.import_module(
            "core.migrations.0067_import_device_accesses"
        ).import_accesses
        migrate(apps, SimpleNamespace(connection=connection))
        migrate(apps, SimpleNamespace(connection=connection))
        self.assertEqual(DeviceAccess.objects.count(), 1)
        access = DeviceAccess.objects.get()
        self.assertEqual(access.token_family, family)
        self.assertIsNotNone(access.last_renewed_at)

    def test_access_status_reports_expiry_and_external_revocation(self):
        from core.models import DeviceAccess
        from oauth2_provider.models import RefreshToken, AccessToken
        from rest_framework.test import APIClient

        device = self.start()
        self.approve(device)
        tokens = self.poll(device).json()
        browser = APIClient()
        browser.force_login(self.user)
        RefreshToken.objects.filter(token=tokens["refresh_token"]).update(
            created=timezone.now() - timedelta(days=31)
        )
        AccessToken.objects.filter(token=tokens["access_token"]).update(
            expires=timezone.now() - timedelta(days=1)
        )
        self.assertEqual(
            browser.get("/api/device-access/").data[0]["status"], "expired"
        )
        # External token revocation is reflected even without a management timestamp.
        RefreshToken.objects.get(token=tokens["refresh_token"]).revoke()
        self.assertIsNone(DeviceAccess.objects.get().revoked_at)
        self.assertEqual(
            browser.get("/api/device-access/").data[0]["status"], "revoked"
        )

    def test_code_lifetime_is_fifteen_minutes(self):
        device = self.start()
        self.assertEqual(device["expires_in"], 900)
        self.assertEqual(device["user_code_max_attempts"], 3)
        grant = DeviceGrant.objects.get(device_code=device["device_code"])
        self.assertAlmostEqual(
            (grant.expires - timezone.now()).total_seconds(), 900, delta=3
        )
        self.assertIn("?request=", device["verification_uri"])
        self.assertNotIn(device["device_code"], device["verification_uri"])

    @override_settings(PZSERVER_DEVICE_MAX_CODE_ERRORS=2)
    def test_configured_code_error_limit_is_enforced_and_advertised(self):
        from django.conf import settings

        device = self.start()
        self.assertEqual(device["user_code_max_attempts"], 2)
        self.browser.force_login(self.user)
        page = self.browser.get(device["verification_uri"])
        self.assertContains(page, "up to 2 incorrect code entries")
        csrf = self.browser.cookies[settings.CSRF_COOKIE_NAME].value
        for remaining in (1, 0):
            response = self.browser.post(
                device["verification_uri"],
                {"user_code": "WRONG", "csrfmiddlewaretoken": csrf},
            )
            self.assertEqual(response.status_code, 400)
            self.assertContains(
                response,
                f"{remaining} attempts remaining"
                if remaining
                else "blocked after 2 incorrect codes",
                status_code=400,
            )
        self.assertEqual(self.poll(device).json()["error"], "access_denied")

    def test_three_wrong_codes_block_only_that_request_across_sessions(self):
        from core.models import DeviceAuthorizationAttempt
        from django.conf import settings

        first, other = self.start(), self.start()
        self.browser.force_login(self.user)
        self.browser.get(first["verification_uri"])
        csrf = self.browser.cookies[settings.CSRF_COOKIE_NAME].value
        for index in range(3):
            # Even another valid request's code must not work in this link.
            result = self.browser.post(
                first["verification_uri"],
                {"user_code": other["user_code"], "csrfmiddlewaretoken": csrf},
            )
            self.assertEqual(result.status_code, 400)
        grant = DeviceGrant.objects.get(device_code=first["device_code"])
        self.assertEqual(grant.status, DeviceGrant.DENIED)
        self.assertEqual(DeviceAuthorizationAttempt.objects.get(grant=grant).errors, 3)
        another_browser = Client()
        another_browser.force_login(self.user)
        self.assertEqual(
            another_browser.post(
                first["verification_uri"], {"user_code": first["user_code"]}
            ).status_code,
            400,
        )
        self.assertEqual(
            another_browser.post(
                self.base + "device/", {"user_code": first["user_code"]}
            ).status_code,
            400,
        )
        self.assertEqual(self.poll(first).json()["error"], "access_denied")
        self.approve(other)
        self.assertEqual(self.poll(other).status_code, 200)

    def test_two_errors_still_allow_correct_code_and_csrf_failure_is_not_counted(self):
        from core.models import DeviceAuthorizationAttempt
        from django.conf import settings

        device = self.start()
        self.browser.force_login(self.user)
        self.browser.get(device["verification_uri"])
        csrf = self.browser.cookies[settings.CSRF_COOKIE_NAME].value
        self.assertEqual(
            self.browser.post(
                device["verification_uri"], {"user_code": "wrong"}
            ).status_code,
            403,
        )
        self.assertEqual(DeviceAuthorizationAttempt.objects.get().errors, 0)
        for _ in range(2):
            self.browser.post(
                device["verification_uri"],
                {"user_code": "wrong", "csrfmiddlewaretoken": csrf},
            )
        self.approve(device)
        self.assertEqual(self.poll(device).status_code, 200)

    def test_cancel_requires_private_code_and_invalidates_unredeemed_approval(self):
        device = self.start()
        bad = self.post(
            self.base + "cancel/",
            {"client_id": self.app.client_id, "device_code": "wrong"},
        )
        self.assertEqual(bad.status_code, 200)
        self.assertEqual(
            DeviceGrant.objects.get().status, DeviceGrant.AUTHORIZATION_PENDING
        )
        self.approve(device)
        cancel = self.post(
            self.base + "cancel/",
            {"client_id": self.app.client_id, "device_code": device["device_code"]},
        )
        self.assertEqual(cancel.status_code, 200)
        self.assertEqual(self.poll(device).json()["error"], "access_denied")

    @override_settings(PZSERVER_DEVICE_RATE_LIMIT_RETENTION_SECONDS=60)
    def test_prune_command_uses_configured_counter_retention(self):
        from core.models import DeviceRateLimit
        from django.core.management import call_command

        old = DeviceRateLimit.objects.create(key="old", count=1)
        recent = DeviceRateLimit.objects.create(key="recent", count=1)
        DeviceRateLimit.objects.filter(pk=old.pk).update(
            started_at=timezone.now() - timedelta(seconds=61)
        )
        call_command("prune_device_authorizations", verbosity=0)
        self.assertFalse(DeviceRateLimit.objects.filter(pk=old.pk).exists())
        self.assertTrue(DeviceRateLimit.objects.filter(pk=recent.pk).exists())

    def test_form_origin_is_preserved_and_null_origin_is_rejected(self):
        from django.conf import settings

        device = self.start()
        self.browser.force_login(self.user)
        page = self.browser.get(device["verification_uri"])
        self.assertContains(page, '<meta name="referrer" content="same-origin">')
        csrf = self.browser.cookies[settings.CSRF_COOKIE_NAME].value
        data = {"user_code": device["user_code"], "csrfmiddlewaretoken": csrf}
        rejected = self.browser.post(
            device["verification_uri"], data, HTTP_ORIGIN="null"
        )
        self.assertEqual(rejected.status_code, 403)
        accepted = self.browser.post(
            device["verification_uri"], data, HTTP_ORIGIN="http://testserver"
        )
        self.assertEqual(accepted.status_code, 302)
        approved = self.browser.post(
            accepted.url,
            {"action": "accept", "csrfmiddlewaretoken": csrf},
            HTTP_ORIGIN="http://testserver",
        )
        self.assertEqual(approved.status_code, 302)

    def test_device_pages_show_account_and_preserve_consent_actions(self):
        device = self.start()
        self.browser.force_login(self.user)
        page = self.browser.get(device["verification_uri"])
        self.assertContains(page, "Enter your authorization code")
        self.assertContains(page, self.user.username)
        self.assertContains(page, 'name="csrfmiddlewaretoken"')
        self.approve(device)
        status = self.browser.get(
            self.base
            + f"device-grant-status/{self.app.client_id}/{device['user_code']}"
        )
        self.assertContains(status, "Your environment is authorized")
        denied = self.start()
        self.approve(denied, "deny")
        status = self.browser.get(
            self.base
            + f"device-grant-status/{self.app.client_id}/{denied['user_code']}"
        )
        self.assertContains(status, "Access was not granted")

    def test_approval_token_api_refresh_and_revoke(self):
        device = self.start()
        self.assertEqual(self.browser.get(self.base + "device/").status_code, 302)
        self.approve(device)
        response = self.poll(device)
        self.assertEqual(response.status_code, 200, response.content)
        token = response.json()
        self.assertEqual(set(token["scope"].split()), {"read", "write"})
        protected = self.client.get(
            "/protected/", HTTP_AUTHORIZATION="Bearer " + token["access_token"]
        )
        self.assertEqual(protected.json(), {"username": "alice"})
        refreshed = self.post(
            self.base + "token/",
            {
                "client_id": self.app.client_id,
                "grant_type": "refresh_token",
                "refresh_token": token["refresh_token"],
            },
        )
        self.assertEqual(refreshed.status_code, 200, refreshed.content)
        access = refreshed.json()["access_token"]
        revoked = self.post(
            self.base + "revoke_token/",
            {"client_id": self.app.client_id, "token": access},
        )
        self.assertEqual(revoked.status_code, 200)
        self.assertEqual(
            self.client.get(
                "/protected/", HTTP_AUTHORIZATION="Bearer " + access
            ).status_code,
            401,
        )

    def test_pending_denied_and_expired_requests(self):
        device = self.start()
        self.assertEqual(self.poll(device).json()["error"], "authorization_pending")
        denied = self.start()
        self.approve(denied, "deny")
        self.assertEqual(self.poll(denied).json()["error"], "access_denied")

    def test_expired_device_code_is_rejected(self):
        expired = self.start()
        DeviceGrant.objects.filter(user_code=expired["user_code"]).update(
            expires=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(self.poll(expired).json()["error"], "expired_token")

    def test_legacy_password_flow_still_works(self):
        app = Application.objects.create(
            name="Existing web client",
            client_type=Application.CLIENT_CONFIDENTIAL,
            client_id="legacy-web",
            client_secret="test-secret",
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        response = self.post(
            "/api/auth/token",
            {
                "client_id": app.client_id,
                "client_secret": "test-secret",
                "grant_type": "password",
                "username": "alice",
                "password": "test-password",
                "scope": "read write",
            },
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.json()["expires_in"], 600)

    def test_device_code_is_single_use(self):
        device = self.start()
        self.approve(device)
        self.assertEqual(self.poll(device).status_code, 200)
        self.assertNotEqual(self.poll(device).status_code, 200)

    def test_polling_interval_is_enforced(self):
        device = self.start()
        self.assertEqual(self.poll(device).json()["error"], "authorization_pending")
        self.assertEqual(self.poll(device).json()["error"], "slow_down")

    def test_legacy_endpoint_cannot_bypass_device_guards(self):
        device = self.start()
        self.approve(device)
        for suffix in ("token", "token/"):
            response = self.post(
                "/api/auth/" + suffix,
                {
                    "client_id": self.app.client_id,
                    "device_code": device["device_code"],
                    "grant_type": Application.GRANT_DEVICE_CODE,
                },
            )
            self.assertEqual(response.json()["error"], "unsupported_grant_type")
        self.assertEqual(self.poll(device).status_code, 200)

    def test_wrong_client_and_missing_code_do_not_consume_grant(self):
        device = self.start()
        self.approve(device)
        other = Application.objects.create(
            name="Other",
            client_id="other",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_DEVICE_CODE,
        )
        for data in (
            {"client_id": other.client_id, "device_code": device["device_code"]},
            {"client_id": self.app.client_id},
        ):
            response = self.post(
                self.base + "token/",
                {"grant_type": Application.GRANT_DEVICE_CODE, **data},
            )
            self.assertEqual(response.status_code, 400)
        self.assertEqual(self.poll(device).status_code, 200)

    def test_slow_down_increases_interval_and_recovery(self):
        from unittest.mock import patch

        device = self.start()
        self.poll(device)
        self.assertEqual(self.poll(device).json()["error"], "slow_down")
        grant = DeviceGrant.objects.get(device_code=device["device_code"])
        self.assertEqual(grant.interval, device["interval"] + 5)
        with patch(
            "core.views.device_oauth.timezone.now",
            return_value=grant.last_checked + timedelta(seconds=grant.interval),
        ):
            self.assertEqual(self.poll(device).json()["error"], "authorization_pending")

    def test_approved_but_expired_code_cannot_issue_token(self):
        device = self.start()
        self.approve(device)
        DeviceGrant.objects.filter(device_code=device["device_code"]).update(
            expires=timezone.now() - timedelta(seconds=1)
        )
        self.assertEqual(self.poll(device).json()["error"], "expired_token")

    def test_failed_issuance_rolls_back_token_and_keeps_code(self):
        from unittest.mock import patch
        from oauth2_provider.models import AccessToken
        from oauth2_provider.views import TokenView

        device = self.start()
        self.approve(device)
        original = TokenView.post

        def fail_after_issuance(view, request, *args, **kwargs):
            response = original(view, request, *args, **kwargs)
            self.assertEqual(response.status_code, 200)
            raise RuntimeError("simulated issuance failure")

        with patch.object(TokenView, "post", fail_after_issuance):
            with self.assertRaises(RuntimeError):
                self.poll(device)
        self.assertFalse(AccessToken.objects.filter(application=self.app).exists())
        self.assertTrue(
            DeviceGrant.objects.filter(device_code=device["device_code"]).exists()
        )
        self.assertEqual(self.poll(device).status_code, 200)

    def test_inactive_user_cannot_redeem_approved_code(self):
        device = self.start()
        self.approve(device)
        self.user.is_active = False
        self.user.save()
        self.assertEqual(self.poll(device).json()["error"], "access_denied")


@skipUnless(DeviceGrant is not None, "Requires Django OAuth Toolkit 3.4.1")
@override_settings(ROOT_URLCONF=__name__)
class DeviceConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="parallel-user")
        self.app = Application.objects.create(
            name="Concurrent client",
            client_id="parallel-client",
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_DEVICE_CODE,
        )

    def race(self, status):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections

        grant = DeviceGrant.objects.create(
            client_id=self.app.client_id,
            user=self.user,
            user_code="TESTCODE",
            device_code="private-test-device-code",
            scope="read write",
            status=status,
            expires=timezone.now() + timedelta(minutes=5),
            interval=5,
        )
        DeviceGrant.objects.filter(pk=grant.pk).update(
            last_checked=timezone.now() - timedelta(seconds=10)
        )
        start = Barrier(2)

        def poll():
            try:
                start.wait(timeout=10)
                response = Client().post(
                    "/api/device-oauth/token/",
                    urlencode(
                        {
                            "client_id": self.app.client_id,
                            "device_code": grant.device_code,
                            "grant_type": Application.GRANT_DEVICE_CODE,
                        }
                    ),
                    content_type="application/x-www-form-urlencoded",
                )
                return response.status_code, response.json()
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(poll) for _ in range(2)]
            return [future.result(timeout=20) for future in futures]

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_redemption_issues_only_one_token(self):
        from oauth2_provider.models import AccessToken, RefreshToken

        results = self.race(DeviceGrant.AUTHORIZED)
        self.assertEqual(sorted(status for status, _ in results), [200, 400])
        self.assertEqual(
            [data["error"] for status, data in results if status == 400],
            ["invalid_grant"],
        )
        self.assertEqual(AccessToken.objects.filter(application=self.app).count(), 1)
        self.assertEqual(RefreshToken.objects.filter(application=self.app).count(), 1)
        self.assertFalse(DeviceGrant.objects.exists())

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_pending_polls_share_rate_limit(self):
        results = self.race(DeviceGrant.AUTHORIZATION_PENDING)
        self.assertEqual(
            sorted(data["error"] for _, data in results),
            ["authorization_pending", "slow_down"],
        )
        self.assertEqual(DeviceGrant.objects.get().interval, 10)

    @skipUnlessDBFeature("has_select_for_update")
    def test_refresh_racing_revoke_cannot_restore_access(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections
        from core.models import DeviceAccess
        from oauth2_provider.models import AccessToken, RefreshToken

        tokens = next(
            data for status, data in self.race(DeviceGrant.AUTHORIZED) if status == 200
        )
        access = DeviceAccess.objects.get()
        browser = Client()
        browser.force_login(self.user)
        start = Barrier(2)

        def refresh():
            try:
                start.wait(timeout=10)
                return (
                    Client()
                    .post(
                        "/api/device-oauth/token/",
                        urlencode(
                            {
                                "client_id": self.app.client_id,
                                "grant_type": "refresh_token",
                                "refresh_token": tokens["refresh_token"],
                            }
                        ),
                        content_type="application/x-www-form-urlencoded",
                    )
                    .status_code
                )
            finally:
                connections.close_all()

        def revoke():
            try:
                start.wait(timeout=10)
                return browser.delete(f"/api/device-access/{access.pk}/").status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            first, second = executor.submit(refresh), executor.submit(revoke)
            self.assertIn(first.result(timeout=20), (200, 400))
            self.assertEqual(second.result(timeout=20), 204)
        access.refresh_from_db()
        self.assertIsNotNone(access.revoked_at)
        self.assertFalse(AccessToken.objects.filter(application=self.app).exists())
        self.assertFalse(
            RefreshToken.objects.filter(
                application=self.app, revoked__isnull=True
            ).exists()
        )

    @skipUnlessDBFeature("has_select_for_update")
    def test_concurrent_wrong_codes_do_not_exceed_three_attempts(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections
        from core.models import DeviceAuthorizationAttempt

        grant = DeviceGrant.objects.create(
            client_id=self.app.client_id,
            user_code="RIGHT123",
            device_code="private-code",
            scope="read write",
            status=DeviceGrant.AUTHORIZATION_PENDING,
            expires=timezone.now() + timedelta(minutes=15),
            interval=5,
        )
        attempt = DeviceAuthorizationAttempt.objects.create(grant=grant, errors=2)
        browsers = [Client(), Client()]
        for browser in browsers:
            browser.force_login(self.user)
        start = Barrier(2)

        def wrong(browser):
            try:
                start.wait(timeout=10)
                return browser.post(
                    f"/api/device-oauth/device/?request={attempt.pk}",
                    {"user_code": "WRONG"},
                ).status_code
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(wrong, browsers))
        self.assertEqual(results, [400, 400])
        attempt.refresh_from_db()
        grant.refresh_from_db()
        self.assertEqual(attempt.errors, 3)
        self.assertEqual(grant.status, DeviceGrant.DENIED)

    @skipUnlessDBFeature("has_select_for_update")
    def test_rate_limit_cannot_be_bypassed_by_parallel_workers(self):
        from concurrent.futures import ThreadPoolExecutor
        from threading import Barrier
        from django.db import connections
        from core.device_limits import consume

        start = Barrier(2)

        def request(_):
            try:
                start.wait(timeout=10)
                return consume("test", "same-origin", 1, 60)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(request, range(2)))
        self.assertEqual(sum(value == 0 for value in results), 1)
        self.assertEqual(sum(value > 0 for value in results), 1)
