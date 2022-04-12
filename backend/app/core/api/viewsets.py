from rest_framework import viewsets
from core.api import serializers
from core import models
import os


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ProductType.objects.all()
    serializer_class = serializers.ProductTypeSerializer


class ReleaseViewSet(viewsets.ModelViewSet):
    queryset = models.Release.objects.all()
    serializer_class = serializers.ReleaseSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = models.Product.objects.all()
    serializer_class = serializers.ProductSerializer

    def perform_create(self, serializer):
        main_file = self.request.data.get("main_file")
        file_size = main_file.size
        file_name, file_extension = os.path.splitext(main_file.name)

        serializer.save(
            file_size=file_size, file_name=file_name,
            file_extension=file_extension
        )
