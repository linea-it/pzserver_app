from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from oauth2_provider.models import AccessToken, Application, RefreshToken
from rest_framework.test import APIClient


@override_settings(PZSERVER_WEB_CLIENT_ID="web-bridge-test")
class SessionOAuthBridgeTests(TestCase):
    def test_session_cookies_contain_usable_persisted_tokens(self):
        user = get_user_model().objects.create_user(username="session-user")
        app = Application.objects.create(
            name="Web",
            client_id="web-bridge-test",
            client_secret="test-secret",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        browser = APIClient(enforce_csrf_checks=True)
        browser.force_login(user)
        from django.middleware.csrf import get_token
        from django.test import RequestFactory

        request = RequestFactory().get("/")
        csrf = get_token(request)
        browser.cookies[settings.CSRF_COOKIE_NAME] = request.META["CSRF_COOKIE"]
        response = browser.post(
            "/api/csrf_oauth/",
            {"client_id": app.client_id},
            format="json",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(response.status_code, 302)
        access = response.cookies["pzserver.access_token"].value
        refresh = response.cookies["pzserver.refresh_token"].value
        access_record = AccessToken.objects.get(token=access)
        self.assertEqual(access_record.user, user)
        self.assertTrue(
            RefreshToken.objects.filter(
                token=refresh, access_token=access_record
            ).exists()
        )
        api = APIClient()
        result = api.post("/api/logged_user/", HTTP_AUTHORIZATION="Bearer " + access)
        self.assertEqual(result.status_code, 200, result.data)
        self.assertEqual(result.data["username"], "session-user")
        renewed = api.post(
            "/api/auth/token",
            {
                "client_id": app.client_id,
                "client_secret": "test-secret",
                "grant_type": "refresh_token",
                "refresh_token": refresh,
            },
        )
        self.assertEqual(renewed.status_code, 200, renewed.content)

    def test_session_cannot_issue_tokens_for_other_clients(self):
        user = get_user_model().objects.create_user(username="isolated-session")
        browser = APIClient()
        browser.force_login(user)
        for grant in (Application.GRANT_DEVICE_CODE, Application.GRANT_PASSWORD):
            app = Application.objects.create(
                client_id="other-" + grant,
                client_type=Application.CLIENT_PUBLIC,
                authorization_grant_type=grant,
            )
            response = browser.post("/api/csrf_oauth/", {"client_id": app.client_id})
            self.assertEqual(response.status_code, 400)
            self.assertFalse(AccessToken.objects.filter(application=app).exists())
            self.assertFalse(RefreshToken.objects.filter(application=app).exists())

    @override_settings(PZSERVER_WEB_CLIENT_ID="device-as-web")
    def test_misconfigured_web_id_cannot_allow_device_client(self):
        user = get_user_model().objects.create_user(username="misconfigured-session")
        browser = APIClient()
        browser.force_login(user)
        Application.objects.create(
            client_id="device-as-web", client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_DEVICE_CODE,
        )
        response = browser.post("/api/csrf_oauth/", {"client_id": "device-as-web"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(AccessToken.objects.count(), 0)

    def test_social_conversion_rejects_device_client(self):
        app = Application.objects.create(
            client_id="device-conversion", client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_DEVICE_CODE,
        )
        for endpoint in ("/api/auth/convert-token", "/api/auth/convert-token/"):
            response = APIClient().post(endpoint, {
                "client_id": app.client_id, "grant_type": "convert_token",
                "backend": "example", "token": "example",
            })
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()["error"], "unauthorized_client")
        self.assertEqual(AccessToken.objects.count(), 0)
