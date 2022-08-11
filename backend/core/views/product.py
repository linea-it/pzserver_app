import logging
import os
import mimetypes

from core.models import Product
from core.serializers import ProductSerializer
from core.views.registry_product import RegistryProduct
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse

# from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser


class ProductFilter(filters.FilterSet):
    # TODO: Adicionar Mais Filtros
    # Talvez filtro pelos internal_names de release e product_type

    release__isnull = filters.BooleanFilter(field_name="release", lookup_expr="isnull")

    class Meta:
        model = Product
        fields = [
            "internal_name",
            "release",
            "product_type",
            "official_product",
            "status",
        ]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = [
        "display_name",
    ]
    filterset_class = ProductFilter
    ordering_fields = [
        "id",
        "display_name",
        "product_type",
        "created_at",
    ]
    ordering = ["-created_at"]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        try:
            product = Product.objects.get(pk=instance.pk)

            # Cria um internal name
            name = self.get_internal_name(product.display_name)
            product.internal_name = f"{product.pk}_{name}"
            product.save()

            data = self.get_serializer(instance=product).data
            return Response(data, status=status.HTTP_201_CREATED)

        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        """Adiciona usuario e internal name."""
        # Usuario que fez o upload
        uploaded_by = self.request.user

        return serializer.save(
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

    @action(methods=["GET"], detail=True)
    def download(self, request, **kwargs):
        """Download product"""

        att = self.get_object()
        file_handle = att.main_file.open()

        mimetype, _ = mimetypes.guess_type(att.main_file.path)
        response = FileResponse(file_handle, content_type=mimetype)
        response["Content-Length"] = att.file_size
        response["Content-Disposition"] = "attachment; filename={}".format(
            att.file_name
        )
        return response

    @action(methods=["Post", "Get"], detail=True)
    def registry(self, request, **kwargs):
        """Registry product"""

        try:
            instance = self.get_object()

            rp = RegistryProduct(instance.pk)
            rp.registry()

            # Alterar o status para Registrado
            product = Product.objects.get(pk=instance.pk)
            # Retorna o produto
            data = self.get_serializer(instance=product).data
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            # Altera o status do produto para falha
            # TODO: guardar a causa do erro para debug
            instance.status = 9
            instance.save()
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["Get"], detail=False)
    def pending_publication(self, request, **kwargs):
        """Pending publication"""

        try:
            # Procura por produtos criados pelo usuario que ainda não foram publicados
            product = Product.objects.filter(status=0, user_id=request.user.id).first()

            if product:
                # Retorna o produto
                data = self.get_serializer(instance=product).data
                return Response({"product": data}, status=status.HTTP_200_OK)
            else:
                return Response({"product": None}, status=status.HTTP_200_OK)

        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
