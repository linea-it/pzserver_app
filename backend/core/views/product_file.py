import os

from core.models import ProductFile
from core.serializers import ProductFileSerializer
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response


class ProductFileViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    filterset_fields = ("id", "product_id")
    ordering_fields = ["id", "role"]
    ordering = ["id"]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        data = self.get_serializer(instance=instance).data
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """Adiciona size, name, extension."""

        file = self.request.data.get("file")
        size = file.size
        filename, extension = os.path.splitext(file.name)

        return serializer.save(
            size=size,
            name=file.name,
            extension=extension,
        )
