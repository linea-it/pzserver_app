import logging
import os

from core.models import Product
from core.serializers import ProductSerializer
from core.views.registry_product import RegistryProduct
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.response import Response

# from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser


class ProductFilter(filters.FilterSet):
    # TODO: Adicionar Mais Filtros
    # Talvez filtro pelos internal_names de release e product_type
    no_release = filters.BooleanFilter(field_name='release', lookup_expr='isnull')

    class Meta:
        model = Product
        fields = ["internal_name", "release", "no_release", "product_type", "official_product"]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    search_fields = ["display_name", "file_name"]
    filterset_class = ProductFilter
    ordering_fields = [
        "id",
        "display_name",
        "product_type",
        "created_at",
        "file_name",
        "file_size",
    ]
    ordering = ["-created_at"]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        try:
            rp = RegistryProduct(instance.pk)
            rp.registry()

            product = Product.objects.get(pk=instance.pk)
            data = self.get_serializer(instance=product).data
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            # Apaga o registro que acabou de ser criado.
            # TODO: provavelmente seria melhor alterar um status para falha
            # e guardar a causa do erro para debug
            instance.delete()
            # TODO: Remover os arquivos
            # TODO: Implementar tratamento de erro.
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """Executa antes do create
        adiciona usuario e internal name.
        """
        data = self.request.data

        # Internal Name
        internal_name = self.get_internal_name(data.get("display_name"))

        # Usuario que fez o upload
        uploaded_by = self.request.user

        return serializer.save(
            internal_name=internal_name,
            user=uploaded_by,
        )

    def get_internal_name(self, display_name):
        """
        Cria um internal name sem caracteres especiais
        e nem espaços.
        o internal name pode ser usado para paths, urls e tablenames.
        """
        # troca espacos por "_", converte para lowercase, remove espacos do final
        name = display_name.replace(" ", "_").lower().strip().strip("\n")

        # Retirar qualquer caracter que nao seja alfanumerico exceto "_"
        name = "".join(e for e in name if e.isalnum() or e == "_")

        return name
