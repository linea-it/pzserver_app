from datetime import timedelta

from core.models import DeviceAccess
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.models import get_refresh_token_model
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


class DeviceAccessView(APIView):
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def initial(self, request, *args, **kwargs):
        header = get_authorization_header(request).split()
        if header and header[0].lower() != b"bearer":
            raise PermissionDenied(
                "Sign in to PzServer to manage connected applications."
            )
        super().initial(request, *args, **kwargs)
        application = request.auth.application if request.auth is not None else None
        if not request.user.is_active or (
            request.auth is not None
            and (
                application is None
                or application.client_id
                != getattr(settings, "PZSERVER_WEB_CLIENT_ID", "")
                or application.authorization_grant_type
                == "urn:ietf:params:oauth:grant-type:device_code"
            )
        ):
            raise PermissionDenied(
                "Sign in to PzServer to manage connected applications."
            )

    def get(self, request, access_id=None):
        if access_id is not None:
            raise MethodNotAllowed("GET")
        accesses = list(
            DeviceAccess.objects.filter(user=request.user).select_related("application")
        )
        # Read only metadata, never token values. Also reflect external OAuth revocation.
        live = {}
        lifetime = timedelta(seconds=settings.PZSERVER_DEVICE_REFRESH_TOKEN_SECONDS)
        for token in (
            get_refresh_token_model()
            .objects.filter(
                user=request.user,
                token_family__in=[a.token_family for a in accesses],
                revoked__isnull=True,
                access_token__isnull=False,
            )
            .values("token_family", "created", "access_token__expires")
        ):
            expiry = max(token["created"] + lifetime, token["access_token__expires"])
            live[token["token_family"]] = max(
                expiry, live.get(token["token_family"], expiry)
            )
        now = timezone.now()

        def access_status(access):
            if access.revoked_at:
                return "revoked"
            if access.token_family in live:
                return "active" if live[access.token_family] > now else "expired"
            if (access.last_renewed_at or access.authorized_at) + lifetime <= now:
                return "expired"
            return "revoked"

        return Response(
            [
                {
                    "id": access.pk,
                    "name": access.name,
                    "application": access.application.name,
                    "authorized_at": access.authorized_at,
                    "last_renewed_at": access.last_renewed_at,
                    "revoked_at": access.revoked_at,
                    "status": access_status(access),
                }
                for access in accesses
            ]
        )

    @transaction.atomic
    def patch(self, request, access_id=None):
        if access_id is None:
            raise MethodNotAllowed("PATCH")
        access = get_object_or_404(
            DeviceAccess.objects.select_for_update(), pk=access_id, user=request.user
        )
        name = request.data.get("name")
        if (
            not isinstance(name, str)
            or not name.strip()
            or len(name.strip()) > 100
            or not name.isprintable()
        ):
            raise ValidationError(
                {"name": "Enter a name between 1 and 100 printable characters."}
            )
        access.name = name.strip()
        access.save(update_fields=["name"])
        return Response({"name": access.name})

    @transaction.atomic
    def delete(self, request, access_id=None):
        if access_id is None:
            raise MethodNotAllowed("DELETE")
        access = get_object_or_404(
            DeviceAccess.objects.select_for_update(), pk=access_id, user=request.user
        )
        # Same lock order as token rotation: access record, then OAuth token rows.
        if access.revoked_at is None:
            access.revoked_at = timezone.now()
            access.save(update_fields=["revoked_at"])
        get_refresh_token_model().revoke_family(access.token_family)
        return Response(status=204)
