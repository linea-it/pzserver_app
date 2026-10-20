from core.models import JupyterHubConsent, TrustedJupyterHub
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.authentication import (
    SessionAuthentication,
    get_authorization_header,
)
from rest_framework.exceptions import (
    MethodNotAllowed,
    PermissionDenied,
    ValidationError,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class HubAccessView(APIView):
    # Personal API tokens and partner tokens cannot grant or revoke consent.
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        parts = get_authorization_header(request).split()
        if parts and parts[0].lower() not in (b"bearer",):
            raise PermissionDenied("Sign in to PzServer to manage JupyterHub access.")
        super().initial(request, *args, **kwargs)
        if not request.user.is_active:
            raise PermissionDenied("Inactive PzServer account.")

    def get(self, request, hub_id=None):
        if hub_id is not None:
            raise MethodNotAllowed("GET")
        consents = {
            c.hub_id: c for c in JupyterHubConsent.objects.filter(user=request.user)
        }
        return Response(
            [
                {
                    "id": hub.pk,
                    "name": hub.name,
                    "public_url": hub.public_url,
                    "available": hub.enabled,
                    "signature": hub.consent_signature,
                    "authorized": bool(
                        consents.get(hub.pk)
                        and consents[hub.pk].enabled
                        and consents[hub.pk].hub_signature == hub.consent_signature
                    ),
                }
                for hub in TrustedJupyterHub.objects.all()
            ]
        )

    @transaction.atomic
    def put(self, request, hub_id=None):
        if hub_id is None:
            raise MethodNotAllowed("PUT")
        enabled = request.data.get("enabled")
        if type(enabled) is not bool:
            raise ValidationError({"enabled": "A boolean is required."})
        hub = get_object_or_404(
            TrustedJupyterHub.objects.select_for_update(), pk=hub_id
        )
        if enabled and not hub.enabled:
            raise ValidationError("This Hub is unavailable.")
        if enabled and request.data.get("signature") != hub.consent_signature:
            raise ValidationError(
                "Hub configuration changed. Reload this page before authorizing."
            )
        consent, _ = JupyterHubConsent.objects.get_or_create(user=request.user, hub=hub)
        consent.enabled = enabled
        if enabled:
            consent.hub_signature = hub.consent_signature
            consent.authorized_at = timezone.now()
            consent.revoked_at = None
        else:
            consent.revoked_at = timezone.now()
        consent.save()
        return Response({"authorized": enabled})
