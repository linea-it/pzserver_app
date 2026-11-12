"""Project-maintained Device Flow guards around unmodified DOT 3.4.1 views."""

import json
import hashlib
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
from uuid import UUID

from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from core.models import DeviceAuthorizationAttempt
from core.device_limits import consume, limited_response

from core.models import DeviceAccess
from oauthlib.oauth2 import InvalidGrantError
from oauth2_provider.models import get_refresh_token_model
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from drf_social_oauth2.views import TokenView as SocialTokenView
from drf_social_oauth2.views import ConvertTokenView as SocialConvertTokenView
from oauthlib.common import Request as OAuthlibRequest
from oauthlib.oauth2.rfc8628 import errors as rfc8628_errors
from oauth2_provider import views
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.models import (
    DeviceCodeResponse,
    DeviceRequest,
    create_device_grant,
    get_application_model,
    get_device_grant_model,
)


def oauth_error(code):
    response = JsonResponse({"error": code}, status=400)
    response["Cache-Control"] = "no-store"
    response["Pragma"] = "no-cache"
    return response


def is_device_client(client):
    return (
        client is not None
        and client.authorization_grant_type == client.GRANT_DEVICE_CODE
    )


class DeviceLifetimeValidator(oauth2_settings.OAUTH2_VALIDATOR_CLASS):
    DEVICE_CODE_AUTHORIZED = "authorized"

    def validate_device_code(self, client_id, code, request, *args, **kwargs):
        """Implement the oauthlib 4.0.1 RFC 8628 validation hook."""
        model = get_device_grant_model()
        try:
            device = model.objects.get(device_code=code, client_id=client_id)
        except model.DoesNotExist:
            return None

        if device.status == model.DENIED:
            return rfc8628_errors.AccessDenied.error
        if device.is_expired():
            return rfc8628_errors.ExpiredTokenError.error
        if device.status == model.AUTHORIZATION_PENDING:
            return rfc8628_errors.AuthorizationPendingError.error
        if device.status != model.AUTHORIZED:
            return None

        request.user = device.user
        request.scopes = device.scope.split() if device.scope else []
        return self.DEVICE_CODE_AUTHORIZED

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        if not super().validate_refresh_token(
            refresh_token, client, request, *args, **kwargs
        ):
            return False
        if is_device_client(client):
            token = request.refresh_token_instance
            lifetime = settings.PZSERVER_DEVICE_REFRESH_TOKEN_SECONDS
            return (
                DeviceAccess.objects.filter(
                    token_family=token.token_family, revoked_at__isnull=True
                ).exists()
                and request.user.is_active
                and token.created + timedelta(seconds=lifetime) > timezone.now()
            )
        return True

    def _save_bearer_token(self, token, request, *args, **kwargs):
        if not is_device_client(request.client):
            return super()._save_bearer_token(token, request, *args, **kwargs)
        # DOT wraps this hook in a transaction. Serialize renewal with revocation.
        previous = getattr(request, "refresh_token_instance", None)
        access = None
        if previous is not None:
            access = (
                DeviceAccess.objects.select_for_update()
                .filter(
                    token_family=previous.token_family,
                    user=request.user,
                    application=request.client,
                )
                .first()
            )
            if access is None or access.revoked_at is not None:
                raise InvalidGrantError()
        result = super()._save_bearer_token(token, request, *args, **kwargs)
        refresh = get_refresh_token_model().objects.get(
            token_checksum=hashlib.sha256(token["refresh_token"].encode()).hexdigest(),
            revoked__isnull=True,
        )
        if access is None:
            DeviceAccess.objects.create(
                token_family=refresh.token_family,
                user=request.user,
                application=request.client,
                name=(request.client.name or "Python access")[:100],
                authorized_at=refresh.created,
            )
        else:
            access.last_renewed_at = refresh.created
            access.save(update_fields=["last_renewed_at"])
        return result

    def rotate_refresh_token(self, request):
        if is_device_client(request.client):
            return True
        return super().rotate_refresh_token(request)


class DeviceLifetimeMixin:
    validator_class = DeviceLifetimeValidator

    @classmethod
    def get_oauthlib_core(cls):
        # Never inherit a core cached by the legacy parent view: it lacks our validator.
        if (
            "_oauthlib_core" not in cls.__dict__
            or oauth2_settings.ALWAYS_RELOAD_OAUTHLIB_CORE
        ):
            cls._oauthlib_core = cls.get_oauthlib_backend_class()(cls.get_server())
        return cls._oauthlib_core

    @classmethod
    def get_server(cls):
        kwargs = dict(oauth2_settings.server_kwargs)
        original = kwargs.get(
            "token_expires_in", oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
        )

        def expires_in(request):
            if is_device_client(request.client):
                return settings.PZSERVER_DEVICE_ACCESS_TOKEN_SECONDS
            return original(request) if callable(original) else original

        kwargs["token_expires_in"] = expires_in
        return cls.get_server_class()(cls.get_validator_class()(), **kwargs)


class DeviceAuthorizationView(views.DeviceAuthorizationView):
    def toolkit_post(self, request):
        """Create a grant while DOT 3.4.1 catches up with oauthlib 4 responses."""
        headers, payload, status = self.create_device_authorization_response(request)
        if status != 200:
            return JsonResponse(json.loads(payload), status=status, headers=headers)

        client_id = request.POST["client_id"]
        requested_scope = request.POST.get("scope", "").strip()
        if requested_scope:
            scope = requested_scope
        else:
            application = get_application_model().objects.get(client_id=client_id)
            core = self.get_oauthlib_core()
            oauth_request = OAuthlibRequest(
                request.build_absolute_uri(),
                http_method=request.method,
                body=urlencode(core.extract_body(request)),
                headers=core.extract_headers(request),
            )
            oauth_request.client_id = client_id
            oauth_request.client = application
            scope = " ".join(
                core.server.request_validator.get_default_scopes(
                    client_id, oauth_request
                )
            )

        # oauthlib 4.0.1 adds a non-RFC scope field that DOT 3.4.1 does not
        # accept in DeviceCodeResponse. The resolved scope is stored separately.
        payload.pop("scope", None)
        device_response = DeviceCodeResponse(**payload)
        create_device_grant(
            DeviceRequest(client_id=client_id, scope=scope), device_response
        )
        return JsonResponse(payload, status=status, headers=headers)

    def post(self, request, *args, **kwargs):
        # Device clients are public, with client_id in the form body.
        application = get_application_model()
        if not application.objects.filter(
            client_id=request.POST.get("client_id"),
            client_type=application.CLIENT_PUBLIC,
            authorization_grant_type=application.GRANT_DEVICE_CODE,
        ).exists():
            return oauth_error("invalid_client")
        with transaction.atomic():
            response = self.toolkit_post(request)
            if response.status_code == 200:
                data = json.loads(response.content)
                lifetime = settings.PZSERVER_DEVICE_CODE_SECONDS
                now = timezone.now()
                grant = get_device_grant_model().objects.get(
                    device_code=data["device_code"]
                )
                get_device_grant_model().objects.filter(pk=grant.pk).update(
                    expires=now + timedelta(seconds=lifetime),
                    last_checked=now - timedelta(seconds=data.get("interval", 5)),
                )
                attempt = DeviceAuthorizationAttempt.objects.create(grant=grant)
                parsed = urlsplit(data["verification_uri"])
                query = dict(parse_qsl(parsed.query))
                query["request"] = str(attempt.pk)
                data["verification_uri"] = urlunsplit(
                    parsed._replace(query=urlencode(query))
                )
                data.pop("verification_uri_complete", None)
                data["expires_in"] = lifetime
                data["user_code_max_attempts"] = (
                    settings.PZSERVER_DEVICE_MAX_CODE_ERRORS
                )
                response = JsonResponse(data)
                response["Cache-Control"] = "no-store"
                response["Pragma"] = "no-cache"
            return response


class DeviceTokenView(DeviceLifetimeMixin, views.TokenView):
    def post(self, request, *args, **kwargs):
        grant_type = request.POST.get("grant_type")
        if grant_type not in (
            "refresh_token",
            "urn:ietf:params:oauth:grant-type:device_code",
        ):
            return oauth_error("unsupported_grant_type")
        if grant_type == "refresh_token":
            application = get_application_model()
            if not application.objects.filter(
                client_id=request.POST.get("client_id"),
                client_type=application.CLIENT_PUBLIC,
                authorization_grant_type=application.GRANT_DEVICE_CODE,
            ).exists():
                return oauth_error("invalid_client")
            return super().post(request, *args, **kwargs)
        if request.content_type != "application/x-www-form-urlencoded":
            return oauth_error("invalid_request")
        if any(
            len(request.POST.getlist(key)) != 1
            for key in ("client_id", "device_code", "grant_type")
        ):
            return oauth_error("invalid_request")
        model = get_device_grant_model()
        app_model = get_application_model()
        client_id = request.POST["client_id"]
        if not app_model.objects.filter(
            client_id=client_id,
            client_type=app_model.CLIENT_PUBLIC,
            authorization_grant_type=app_model.GRANT_DEVICE_CODE,
        ).exists():
            return oauth_error("invalid_client")
        # Serialize redemption and interval updates across API workers on PostgreSQL.
        with transaction.atomic():
            device = (
                model.objects.select_for_update()
                .filter(
                    device_code=request.POST["device_code"],
                    client_id=client_id,
                )
                .first()
            )
            if device is None:
                return oauth_error("invalid_grant")
            now = timezone.now()
            if device.expires <= now or device.status == model.EXPIRED:
                return oauth_error("expired_token")
            if device.status == model.DENIED:
                return oauth_error("access_denied")
            if now < device.last_checked + timedelta(seconds=device.interval):
                model.objects.filter(pk=device.pk).update(
                    last_checked=now,
                    interval=device.interval + 5,
                )
                return oauth_error("slow_down")
            model.objects.filter(pk=device.pk).update(last_checked=now)
            if device.status == model.AUTHORIZATION_PENDING:
                return oauth_error("authorization_pending")
            if (
                device.status != model.AUTHORIZED
                or not device.user
                or not device.user.is_active
            ):
                return oauth_error("access_denied")
            response = super().post(request, *args, **kwargs)
            if response.status_code == 200:
                # Token issuance and single-use consumption commit together.
                device.delete()
            response["Cache-Control"] = "no-store"
            response["Pragma"] = "no-cache"
            return response


class DeviceUserCodeView(views.DeviceUserCodeView):
    template_name = "pzserver/device/user_code.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["code_minutes"] = settings.PZSERVER_DEVICE_CODE_SECONDS // 60
        context["max_code_errors"] = settings.PZSERVER_DEVICE_MAX_CODE_ERRORS
        return context

    def post(self, request, *args, **kwargs):
        # LoginRequiredMixin runs before this method, and CSRF middleware before dispatch.
        wait = consume(
            "verify-user",
            str(request.user.pk),
            settings.PZSERVER_DEVICE_VERIFY_PER_MINUTE,
            60,
        )
        if wait:
            return limited_response(wait)
        try:
            attempt_id = UUID(request.GET.get("request", ""))
        except (ValueError, TypeError, AttributeError):
            return self.invalid_code(
                "Use the complete authorization link displayed in Python."
            )
        model = get_device_grant_model()
        attempt = DeviceAuthorizationAttempt.objects.filter(pk=attempt_id).first()
        if attempt is None:
            return self.invalid_code(
                "This request is no longer available. Restart login in Python."
            )
        with transaction.atomic():
            # Lock the grant first, consistently with polling, cancellation and approval.
            grant = (
                model.objects.select_for_update().filter(pk=attempt.grant_id).first()
            )
            attempt = (
                DeviceAuthorizationAttempt.objects.select_for_update()
                .filter(pk=attempt_id)
                .first()
            )
            if grant is None or attempt is None:
                return self.invalid_code(
                    "This request is no longer available. Restart login in Python."
                )
            if (
                grant.expires <= timezone.now()
                or grant.status != model.AUTHORIZATION_PENDING
            ):
                return self.invalid_code(
                    "This request expired, was blocked or was already used. Restart login in Python."
                )
            if request.POST.get("user_code", "").strip() != grant.user_code:
                attempt.errors += 1
                attempt.save(update_fields=["errors"])
                max_errors = settings.PZSERVER_DEVICE_MAX_CODE_ERRORS
                remaining = max(0, max_errors - attempt.errors)
                if remaining == 0:
                    grant.status = model.DENIED
                    grant.save(update_fields=["status"])
                return self.invalid_code(
                    f"Incorrect code. {remaining} attempts remaining."
                    if remaining
                    else f"Request blocked after {max_errors} incorrect codes. "
                    "Restart login in Python."
                )
            form = self.get_form()
            if not form.is_valid():
                return self.form_invalid(form)
            form.cleaned_data["device_grant"] = grant
            return super().form_valid(form)

    def invalid_code(self, message):
        form = self.get_form_class()(initial={})
        form.cleaned_data = {}
        form.add_error(None, message)
        return self.render_to_response(self.get_context_data(form=form), status=400)


class DeviceConfirmView(views.DeviceConfirmView):
    template_name = "pzserver/device/accept_deny.html"

    def form_valid(self, form):
        model = get_device_grant_model()
        with transaction.atomic():
            self._device_grant = (
                model.objects.select_for_update()
                .filter(
                    client_id=self.kwargs["client_id"],
                    user_code=self.kwargs["user_code"],
                    user=self.request.user,
                    status=model.AUTHORIZATION_PENDING,
                )
                .first()
            )
            if self._device_grant is None:
                return oauth_error("invalid_grant")
            if self._device_grant.expires <= timezone.now():
                return oauth_error("expired_token")
            return super().form_valid(form)


class WebTokenView(DeviceLifetimeMixin, SocialTokenView):
    def post(self, request, *args, **kwargs):
        # Do not let the pre-existing endpoint bypass the guarded redemption path.
        if (
            request.data.get("grant_type")
            == "urn:ietf:params:oauth:grant-type:device_code"
        ):
            return oauth_error("unsupported_grant_type")
        return super().post(request, *args, **kwargs)


class DeviceGrantStatusView(views.DeviceGrantStatusView):
    template_name = "pzserver/device/status.html"


class WebConvertTokenView(SocialConvertTokenView):
    def post(self, request, *args, **kwargs):
        application = get_application_model()
        if (
            application.objects.filter(
                client_id=request.data.get("client_id"),
                authorization_grant_type=application.GRANT_DEVICE_CODE,
            ).exists()
            or request.data.get("grant_type") == application.GRANT_DEVICE_CODE
        ):
            return oauth_error("unauthorized_client")
        return super().post(request, *args, **kwargs)


@method_decorator(csrf_exempt, name="dispatch")
class DeviceCancelView(View):
    """Cancel an unredeemed request using its private device code as proof."""

    def post(self, request, *args, **kwargs):
        if request.content_type != "application/x-www-form-urlencoded":
            return oauth_error("invalid_request")
        if any(len(request.POST.getlist(k)) != 1 for k in ("client_id", "device_code")):
            return oauth_error("invalid_request")
        with transaction.atomic():
            model = get_device_grant_model()
            grant = (
                model.objects.select_for_update()
                .filter(
                    client_id=request.POST["client_id"],
                    device_code=request.POST["device_code"],
                )
                .first()
            )
            if grant is not None:
                grant.status = model.DENIED
                grant.save(update_fields=["status"])
            response = JsonResponse({"cancelled": True})
            response["Cache-Control"] = "no-store"
            return response
