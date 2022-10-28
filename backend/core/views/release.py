from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from core.serializers import ReleaseSerializer
from core import models


class ReleaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, IsAuthenticatedOrReadOnly]
    queryset = models.Release.objects.all()
    serializer_class = ReleaseSerializer
    ordering = ["-created_at"]
