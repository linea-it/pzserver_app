from rest_framework import viewsets
from core.serializers import ProductTypeSerializer
from core import models


class ProductTypeViewSet(viewsets.ModelViewSet):
    queryset = models.ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    ordering = ["id"]
