from core.models import ProductContent
from core.serializers import ProductContentSerializer
from rest_framework import viewsets

class ProductContentViewSet(viewsets.ModelViewSet):
    queryset = ProductContent.objects.all()
    serializer_class = ProductContentSerializer
    filterset_fields = ("id", "product")
    ordering_fields = [
        "id",
        "order",
    ]
    ordering = ["id"]
