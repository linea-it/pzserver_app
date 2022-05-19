import os

from core.models import Product
from core.serializers import ProductSerializer
from rest_framework import viewsets
from django_filters import rest_framework as filters


class ProductFilter(filters.FilterSet):
    # TODO: Adicionar Mais Filtros
    # Talvez filtro pelos internal_names de release e product_type
    class Meta:
        model = Product
        fields = [
            "release",
            "product_type",
        ]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
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

    def perform_create(self, serializer):
        # Usuario que fez o upload
        uploaded_by = self.request.user
        # Arquivo principal
        main_file = self.request.data.get("main_file")

        # TODO: é interessante guardar os arquivos em diretórios_baseados pelo produt_type
        # E um diretório para cada produto, assim os arquivos de produto e descricao podem
        # ficar juntos e podemos permitir o upload de mais arquivos de um mesmo produto
        # como pdf e exemplode de sitação e coisas do tipo.
        # Exemplo: release->product_type->$id_$name
        # TODO: criar uma regra para o internal name, garantir só string e numeros com um separador unico tipo _
        # TODO: é interessante renomear o arquivo para um nome sem caracteres especiais e sem espacos, por causa do link de download.

        file_size = main_file.size
        file_name, file_extension = os.path.splitext(main_file.name)

        serializer.save(
            user=uploaded_by,
            file_size=file_size,
            file_name=file_name,
            file_extension=file_extension,
        )
