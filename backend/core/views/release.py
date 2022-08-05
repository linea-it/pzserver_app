from rest_framework import viewsets
from core.serializers import ReleaseSerializer
from core import models


class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = models.Release.objects.all()
    serializer_class = ReleaseSerializer
    ordering = ["-created_at"]
