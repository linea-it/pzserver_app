from rest_framework import viewsets
from core.serializers import ProductTypeSerializer
from core import models
from rest_framework.permissions import AllowAny


class ProductTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)
    queryset = models.ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    ordering = ["id"]
