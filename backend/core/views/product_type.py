from core import models
# from rest_framework.permissions import IsAdminUser, IsAuthenticatedOrReadOnly
from core.serializers import ProductTypeSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ProductType.objects.all()
    serializer_class = ProductTypeSerializer
    filterset_fields = [
        "id",
        "name",
    ]
    search_fields = ["display_name", "description"]
    ordering = ["id"]

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)
