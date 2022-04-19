from rest_framework import viewsets
from core.api import serializers
from core import models
from rest_framework.permissions import IsAuthenticated
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
import os


class ProductTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, TokenHasReadWriteScope)
    queryset = models.ProductType.objects.all()
    serializer_class = serializers.ProductTypeSerializer


class ReleaseViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, TokenHasReadWriteScope)
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
