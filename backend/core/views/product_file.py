from rest_framework import viewsets
from core.serializers import ProductFileSerializer
from core.models import ProductFile
import os


class ProductFileViewSet(viewsets.ModelViewSet):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    filter_fields = ("id", "product_id")
    ordering_fields = ["id", "role"]
    ordering = ["id"]

    def perform_create(self, serializer):
        """Adiciona usuario e internal name."""
        data = self.request.data

        file = self.request.data.get("file")
        size = file.size
        filename, extension = os.path.splitext(file.name)

        return serializer.save(
            size=size,
            name=file.name,
            extension=extension,
        )
