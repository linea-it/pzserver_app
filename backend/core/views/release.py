from core import models
from core.serializers import ReleaseSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly


class ReleaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, IsAuthenticatedOrReadOnly]
    queryset = models.Release.objects.all()
    serializer_class = ReleaseSerializer
    filter_fields = [
        "id",
        "name",
    ]
    search_fields = [
        "display_name",
        "description",
    ]
    ordering = ["-created_at"]
