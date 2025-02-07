import logging
import mimetypes
import os
import pathlib
import secrets
import tempfile
import zipfile
from json import loads
from pathlib import Path

from core.models import Product, ProductContent, ProductStatus
from core.product_handle import FileHandle, NotTableError
from core.product_steps import CreateProduct, NonAdminError, RegistryProduct
from core.serializers import ProductSerializer
from core.utils import format_query_to_char
from django.conf import settings
from django.core.paginator import Paginator
from django.http import FileResponse
from django_filters import rest_framework as filters
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

logger = logging.getLogger("django")


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
        fields = {
            "internal_name": ["exact", "in"],
            "display_name": ["exact", "in"],
            "release": ["exact", "in"],
            "product_type": ["exact", "in"],
            "official_product": ["exact", "in"],
            "status": ["exact", "in"],
            "user": ["exact", "in"],
        }

    def filter_user(self, queryset, name, value):
        query = format_query_to_char(
            name, value, ["user__username", "user__first_name", "user__last_name"]
        )

        return queryset.filter(query)

    def filter_name(self, queryset, name, value):
        query = format_query_to_char(name, value, ["display_name"])

        return queryset.filter(query)

    def filter_type_name(self, queryset, name, value):
        query = format_query_to_char(
            name, value, ["product_type__display_name", "product_type__name"]
        )

        return queryset.filter(query)

    def filter_release(self, queryset, name, value):
        query = format_query_to_char(
            name, value, ["release__display_name", "release__name"]
        )
        return queryset.filter(query)


class ProductSpeczViewSet(viewsets.ReadOnlyModelViewSet):
    """Esse endpoint retorna apenas os produtos cujo o product type é = a 'spec-z' e o status é = a 1"""

    queryset = Product.objects.filter(product_type__name="specz_catalog", status=1)
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

        logger.debug("PRODUCT -> %s", request.data)

        try:
            product = CreateProduct(request.data, request.user)
            check_prodtype = product.check_product_types()

            if not check_prodtype.get("success"):
                return Response(
                    check_prodtype.get("message"), status=status.HTTP_400_BAD_REQUEST
                )

            product.save()
            data = self.get_serializer(instance=product.data).data
            return Response(data, status=status.HTTP_201_CREATED)

        except NonAdminError as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["GET"], detail=True)
    def download(self, request, **kwargs):
        """Download product"""
        try:
            product = self.get_object()

            with tempfile.TemporaryDirectory() as tmpdirname:
                # Cria um arquivo zip no diretório tmp com os arquivos do produto
                zip_file = self.zip_product(
                    product.internal_name, product.path, tmpdirname
                )

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
    def download_main_file(self, request, **kwargs):
        """Download product main file"""
        try:
            product = self.get_object()
            main_file = product.files.get(role=0)
            main_file_path = Path(main_file.file.path)
            product_path = pathlib.Path(
                settings.MEDIA_ROOT, product.path, main_file_path
            )

            # Abre o arquivo e envia em bites para o navegador
            mimetype, _ = mimetypes.guess_type(product_path)
            size = product_path.stat().st_size
            name = product_path.name

            file_handle = open(product_path, "rb")
            response = FileResponse(file_handle, content_type=mimetype)

            response["Content-Length"] = size
            response["Content-Disposition"] = "attachment; filename={}".format(name)
            return response
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["GET"], detail=True)
    def read_data(self, request, **kwargs):
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 100))

        product = self.get_object()
        product_file = product.files.get(role=0)
        main_file_path = Path(product_file.file.path)

        try:
            df = FileHandle(main_file_path).to_df()
            records = loads(df.to_json(orient="records"))
            paginator = Paginator(records, page_size)
            records = paginator.get_page(page)

            return Response(
                {
                    "count": df.shape[0],
                    "columns": df.columns,
                    "results": records.object_list,
                }
            )

        except NotTableError as e:
            content = {"message": "Table preview not available for this product type."}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            content = {"message": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)

    @action(methods=["GET"], detail=True)
    def main_file_info(self, request, **kwargs):
        """Get information about the main product file."""
        try:
            product = self.get_object()
            product_file = product.files.get(role=0)
            main_file_path = Path(product_file.file.path)
            product_path = pathlib.Path(
                settings.MEDIA_ROOT, product.path, main_file_path
            )

            data = self.get_serializer(instance=product).data
            main_file = dict()

            main_file["name"] = product_file.name
            main_file["type"] = product_file.type
            main_file["extension"] = product_file.extension
            main_file["size"] = product_file.size
            main_file["n_rows"] = product_file.n_rows

            if product_file.extension == ".csv":
                product_content = FileHandle(product_path)
                main_file["delimiter"] = product_content.handle.delimiter
                main_file["has_header"] = product_content.handle.has_hd
                main_file["columns"] = product_content.handle.column_names

            data["main_file"] = main_file

            return Response(data)
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

    def zip_product(self, internal_name, path, tmpdir):

        product_path = pathlib.Path(settings.MEDIA_ROOT, path)
        thash = "".join(secrets.choice(secrets.token_hex(16)) for i in range(5))
        zip_name = f"{internal_name}_{thash}.zip"
        zip_path = pathlib.Path(tmpdir, zip_name)

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
        """Product can only be deleted by the OWNER or if the user has an
        admin profile.
        """
        # Regra do admin atualizada na issue:
        # 192 - https://github.com/linea-it/pzserver_app/issues/192
        instance = self.get_object()
        if instance.can_delete(self.request.user):
            return super(ProductViewSet, self).destroy(request, pk, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied()

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        data = request.data

        prodstatus = int(data.get("status", 0))
        is_published = ProductStatus(prodstatus).name == "PUBLISHED"

        is_specz = instance.product_type.name == "specz_catalog"
        is_train = instance.product_type.name == "training_set"

        logger.debug(f"Status: {prodstatus}")
        logger.debug(f"IsPubl: {is_published}")

        if is_specz and prodstatus and is_published:
            check_specz = self.__check_mandatory_columns(instance, ["Dec", "RA", "z"])

            if not check_specz.get("success", False):
                content = check_train.get("message")
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        elif is_train and prodstatus and is_published:
            check_train = self.__check_mandatory_columns(instance, ["z"])

            if not check_train.get("success", False):
                content = check_train.get("message")
                return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        instance.status = prodstatus
        instance.save()

        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def __check_mandatory_columns(self, instance, columns):
        """Checks mandatory columns

        Args:
            instance (Product): Product object
            columns (list): mandatory columns
        """

        for prodcont in ProductContent.objects.filter(product=instance.pk):
            if prodcont.alias in columns:
                columns.remove(prodcont.alias)

        if columns:
            return {
                "success": False,
                "message": f"The column(s) was not filled in: {','.join(columns)}",
            }

        return {"success": True, "message": "Mandatory columns filled in."}
