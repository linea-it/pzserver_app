import mimetypes
from django.contrib.auth.models import User
from core.models import Product
from core.serializers import ProductSerializer
from core.views.registry_product import RegistryProduct
from core.product_handle import ProductHandle
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import FileResponse, JsonResponse
import zipfile
import pathlib
from django.conf import settings
import secrets
import os
import pandas as pd
from django.db.models import Q
from pathlib import Path
from rest_framework import exceptions


class ProductFilter(filters.FilterSet):
    release__isnull = filters.BooleanFilter(field_name="release", lookup_expr="isnull")
    uploaded_by__or = filters.CharFilter(method="filter_user")
    uploaded_by = filters.CharFilter(method="filter_user")
    product_type_name__or = filters.CharFilter(method="filter_type_name")
    product_type_name = filters.CharFilter(method="filter_type_name")
    release_name__or = filters.CharFilter(method="filter_release")
    release_name = filters.CharFilter(method="filter_release")
    product_name__or = filters.CharFilter(method="filter_name")
    product_name = filters.CharFilter(method="filter_name")

    class Meta:
        model = Product
        fields = [
            "internal_name",
            "display_name",
            "release",
            "product_type",
            "official_product",
            "status",
            "user",
        ]

    def filter_user(self, queryset, name, value):
        query = self.format_query_to_char(
            name, value, ["user__username", "user__first_name", "user__last_name"]
        )

        return queryset.filter(query)

    def filter_name(self, queryset, name, value):
        query = self.format_query_to_char(name, value, ["display_name"])

        return queryset.filter(query)

    def filter_type_name(self, queryset, name, value):
        query = self.format_query_to_char(name, value, ["product_type__display_name"])

        return queryset.filter(query)

    def filter_release(self, queryset, name, value):
        query = self.format_query_to_char(name, value, ["release__display_name"])
        return queryset.filter(query)

    @staticmethod
    def format_query_to_char(key, value, fields):
        condition = Q.OR if key.endswith("__or") else Q.AND
        values = value.split(",")
        query = Q()

        for value in values:
            subfilter = Q()
            for field in fields:
                subfilter.add(Q(**{f"{field}__icontains": value}), Q.OR)

            query.add(subfilter, condition)

        return query


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    search_fields = [
        "display_name",
        "user__username",
        "user__first_name",
        "user__last_name",
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

            # Verifica se o produto é oficial,
            # Apenas user que fazem parte do Group=Admin podem criar produtos oficiais.
            if product.official_product is True:
                if request.user.profile.is_admin() is False:
                    return Response(
                        {
                            "error": "Not allowed. Only users with admin permissions can create official products."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            # Cria um internal name
            name = self.get_internal_name(product.display_name)
            product.internal_name = f"{product.pk}_{name}"

            # Cria um path para o produto
            relative_path = f"{product.product_type.name}/{product.internal_name}"
            # TODO: Talves mover a criação do path do produto para a parte do upload dos arquivos.
            path = pathlib.Path(settings.MEDIA_ROOT, relative_path)
            path.mkdir(parents=True, exist_ok=True)

            product.path = relative_path

            # Verificar campos relacionados ao Produt Type.

            # Release is not allowed in Spec-z Catalog
            if (
                product.release is not None
                and product.product_type.name == "specz_catalog"
            ):
                return Response(
                    {"release": ["Release must be null on Spec-z Catalogs products."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Survey is only allowed in Spec-z Catalog
            if (
                product.survey is not None
                and product.product_type.name != "specz_catalog"
            ):
                return Response(
                    {
                        "survey": [
                            f"Survey must be null on {product.product_type.display_name} products."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Pzcode is only allowed in Validations Results and Photo-z Table
            if product.pz_code is not None and product.product_type.name in (
                "validation_set",
                "training_set",
                "specz_catalog",
            ):
                return Response(
                    {
                        "pz_code": [
                            f"Pz Code must be null on {product.product_type.display_name} products."
                        ]
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

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
        try:
            product = self.get_object()

            # Cria um arquivo zip no diretório tmp com os arquivos do produto
            zip_file = self.zip_product(product.internal_name, product.path)

            # Abre o arquivo e envia em bites para o navegador
            mimetype, _ = mimetypes.guess_type(zip_file)
            size = zip_file.stat().st_size
            name = zip_file.name

            file_handle = open(zip_file, "rb")
            response = FileResponse(file_handle, content_type=mimetype)
            response["Content-Length"] = size
            response["Content-Disposition"] = "attachment; filename={}".format(name)
            return response

        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["GET"], detail=True)
    def content(self, request, **kwargs):
        """Content product"""
        try:
            product = self.get_object()
            main_file = product.files.get(role=0)
            main_file_path = Path(main_file.file.path)
            product_path = pathlib.Path(
                settings.MEDIA_ROOT, product.path, main_file_path
            )
            product_content = pd.DataFrame.to_dict(
                ProductHandle().df_from_file(product_path)
            )
            return JsonResponse(product_content, safe=False, status=status.HTTP_200_OK)
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    def zip_product(self, internal_name, path):

        product_path = pathlib.Path(settings.MEDIA_ROOT, path)
        zip_name = f"{internal_name}_{secrets.token_urlsafe(8)}.zip"
        zip_path = pathlib.Path(settings.MEDIA_ROOT, "tmp", zip_name)

        with zipfile.ZipFile(
            zip_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as ziphandle:
            for root, dirs, files in os.walk(product_path):
                for file in files:
                    origin_file = os.path.join(root, file)
                    ziphandle.write(origin_file, arcname=file)

        ziphandle.close()

        return zip_path

    def destroy(self, request, pk=None, *args, **kwargs):
        # TODO: Duvida, Admin pode remover produto que não seja dele?
        instance = self.get_object()
        if self.request.user.id == instance.user.pk:
            return super(ProductViewSet, self).destroy(request, pk, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied()
