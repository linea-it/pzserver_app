from core import models
from core.serializers import ReleaseSerializer
from rest_framework import viewsets

# from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from core.serializers import ReleaseSerializer
from core import models


class ReleaseViewSet(viewsets.ModelViewSet):
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
