from core.models import ProductContent
from core.serializers import ProductContentSerializer
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

class ProductContentViewSet(viewsets.ModelViewSet):
    queryset = ProductContent.objects.all()
    serializer_class = ProductContentSerializer
    filterset_fields = ("id", "product")
    ordering_fields = [
        "id",
        "order",
    ]
    ordering = ["id"]

    @action(detail=True, methods=['patch'])
    def update_alias(self, request, pk=None):
        product_content = self.get_object()
        alias = request.data.get('alias')

        if alias is not None:
            product_content.alias = alias
            product_content.save()

            serializer = self.get_serializer(product_content)
            return Response(serializer.data)
        else:
            return Response({'error': 'Alias value is required.'}, status=400)
