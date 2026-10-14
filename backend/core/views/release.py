import logging
from collections.abc import Mapping

import requests
from core import models
from core.maestro import Maestro
from core.permissions import AccessControlMixin, ReleaseAccessPermission
from core.serializers import ReleaseHatsConfigSerializer, ReleaseSerializer
from core.services.hats_config import HatsConfigPolicyError, sanitize_for_frontend
from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


LOGGER = logging.getLogger("django")


class ReleaseViewSet(AccessControlMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Release.objects.all()
    serializer_class = ReleaseSerializer
    permission_classes = [ReleaseAccessPermission]
    filterset_fields = [
        "id",
        "name",
    ]
    search_fields = [
        "display_name",
        "description",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        """
        Filters releases based on the authenticated user's access groups.
        """
        return self.get_accessible_releases_queryset()

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)

    @extend_schema(responses=ReleaseHatsConfigSerializer)
    @action(methods=["GET"], detail=True, url_path="hats_config")
    def hats_config(self, request, pk=None):
        """Return the editable HATS configuration for an accessible release."""
        release = self.get_object()

        try:
            upstream_data = Maestro(url=settings.ORCHEST_URL).hats_config(release.name)
            if not isinstance(upstream_data, Mapping):
                raise HatsConfigPolicyError(
                    "Orchestration returned an invalid HATS configuration response."
                )
            if "config" not in upstream_data or "last_modified" not in upstream_data:
                raise HatsConfigPolicyError(
                    "Orchestration returned an incomplete HATS configuration response."
                )

            response_data = {
                "release": release.name,
                "last_modified": upstream_data["last_modified"],
                "config": sanitize_for_frontend(upstream_data["config"]),
            }
            serializer = ReleaseHatsConfigSerializer(data=response_data)
            if not serializer.is_valid():
                raise HatsConfigPolicyError(
                    "Orchestration returned invalid HATS configuration metadata."
                )
        except (requests.exceptions.RequestException, HatsConfigPolicyError):
            LOGGER.exception(
                "Could not retrieve HATS configuration for release_id=%s "
                "release_name=%s",
                release.pk,
                release.name,
            )
            return Response(
                {"error": "Could not retrieve the release HATS configuration."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(serializer.validated_data)
