from rest_framework import viewsets
from core.serializers import ProductContentSerializer
from core.models import ProductContent


class ProductContentViewSet(viewsets.ModelViewSet):
    queryset = ProductContent.objects.all()
    serializer_class = ProductContentSerializer
    filter_fields = ("id", "product_id")
    ordering_fields = [
        "id",
        "order",
    ]
    ordering = ["id"]
