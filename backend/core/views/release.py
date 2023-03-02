from core import models
# from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from core.serializers import ReleaseSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ReleaseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Release.objects.all()
    serializer_class = ReleaseSerializer
    filterset_fields = [
        "id",
        "name",
    ]
    search_fields = [
        "display_name",
        "description",
    ]
    ordering = ["-created_at"]

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)
