from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from core.serializers import ProductTypeSerializer
from core import models


class ProductTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser, IsAuthenticatedOrReadOnly]
    queryset = models.ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    ordering = ["id"]
