from core import models
from core.serializers import ProductTypeSerializer
from rest_framework import viewsets

# from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from core.serializers import ProductTypeSerializer
from core import models


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    filterset_fields = [
        "id",
        "name",
    ]
    search_fields = ["display_name", "description"]
    ordering = ["id"]
