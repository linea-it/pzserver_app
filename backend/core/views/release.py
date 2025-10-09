from core import models
from core.permissions import AccessControlMixin, ReleaseAccessPermission
from core.serializers import ReleaseSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


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
