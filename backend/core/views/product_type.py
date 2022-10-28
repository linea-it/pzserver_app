from core import models
from core.serializers import ProductTypeSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly


class ProductTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, IsAuthenticatedOrReadOnly]
    queryset = models.ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    filter_fields = [
        "id",
        "name",
    ]
    search_fields = ["display_name", "description"]
    ordering = ["id"]
