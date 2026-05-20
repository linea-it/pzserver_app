import logging
import mimetypes
import pathlib
import tempfile
from json import dumps, loads
from pathlib import Path

import yaml
from core.models import (
    FileStorageKind,
    Product,
    ProductContent,
    ProductStatus,
    ProductDownloadArchive,
    ProductDownloadArchiveStatus,
)
from core.permissions import AccessControlMixin, ProductAccessPermission
from core.product_handle import FileHandle, NotTableError
from core.product_steps import CreateProduct, NonAdminError, RegistryProduct
from core.serializers import ProductSerializer
from core.services import AccessControlService, ProductDownloadArchiveService
from core.tasks import build_product_download_archive, build_product_table_preview
from core.utils import format_query_to_char
from django.conf import settings
from django.core import signing
from django.core.paginator import Paginator
from django.http import FileResponse, HttpResponse
from django_filters import rest_framework as filters
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.validators import ValidationError

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


class ProductSpeczViewSet(AccessControlMixin, viewsets.ReadOnlyModelViewSet):
    """
    This endpoint returns only those products whose
    product type = 'redshift_catalog' and status = 1
    """

    queryset = Product.objects.filter(product_type__name="redshift_catalog", status=1)
    serializer_class = ProductSerializer
    permission_classes = [ProductAccessPermission]
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

    def get_queryset(self):
        """
        Filters products based on the authenticated user's access groups.
        """
        base_queryset = Product.objects.filter(
            product_type__name="redshift_catalog", status=1
        )
        return AccessControlService.filter_accessible_products(
            self.request.user, base_queryset
        )


class ProductViewSet(AccessControlMixin, viewsets.ModelViewSet):
    TABLE_PREVIEW_PROCESSING_MESSAGE = (
        "Table preview is being processed in the background."
    )

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ProductAccessPermission]
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

    def get_queryset(self):
        """
        Filtra produtos baseado nos grupos de acesso do usuário autenticado.
        """
        return self.get_accessible_products_queryset()

    def create(self, request):

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

        except ValidationError as errors:
            content = {}
            if isinstance(errors.detail, dict):
                for key, value in errors.detail.items():
                    content[key] = value[0]
                _status = status.HTTP_400_BAD_REQUEST
            else:
                content = {"error": str(errors)}
                _status = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(content, status=_status)

        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __get_product_contents(self, product):
        """Get product contents"""
        if not product.contents:
            return []

        contents = []
        for content in product.contents.all():
            if content.alias:
                contents.append(
                    {
                        "column_name": content.column_name,
                        "ucd": content.ucd,
                        "alias": content.alias,
                    }
                )
        return contents

    def __get_full_product(self, product):
        """Get full product data"""
        product_full = self.get_serializer(instance=product).data

        for file in product.files.all():
            if file.role == 0:
                product_full["main_file"] = {
                    "name": file.name,
                    "type": file.type,
                    "extension": file.extension,
                    "size": file.size,
                    "n_rows": file.n_rows,
                }
                product_contents = self.__get_product_contents(product)
                if product_contents:
                    product_full["associated_columns"] = product_contents
            else:
                if not "attach_files" in product_full:
                    product_full["attach_files"] = []
                product_full["attach_files"].append(
                    {"name": file.name, "type": file.type}
                )

        return product_full

    def __get_flag_translation_name(self, config):
        """Extract the flags translation filename from a nested config."""
        if isinstance(config, dict):
            filepath = config.get("flags_translation_file")
            if filepath:
                return Path(filepath).name

            for value in config.values():
                filename = self.__get_flag_translation_name(value)
                if filename:
                    return filename

        if isinstance(config, list):
            for value in config:
                filename = self.__get_flag_translation_name(value)
                if filename:
                    return filename

        return None

    @action(methods=["GET"], detail=True)
    def process_config(self, request, **kwargs):
        product = self.get_object()

        if not hasattr(product, "process"):
            return Response({})

        config = product.process.used_config or {}
        response = {"config": config.get("param", {})}

        flag_translation_name = self.__get_flag_translation_name(config)
        if not flag_translation_name:
            return Response(response)

        flag_translation_path = pathlib.Path(
            settings.MEDIA_ROOT,
            product.path,
            flag_translation_name,
        )

        if flag_translation_path.exists():
            response["flag_translation"] = yaml.safe_load(
                flag_translation_path.read_text(encoding="utf-8")
            )

        return Response(response)

    def __serialize_download_archive(self, archive, request):
        data = {
            "id": archive.pk,
            "task_id": archive.task_id,
            "status": archive.status,
            "filename": archive.filename,
            "size": archive.size,
            "checksum": archive.checksum,
            "source_signature": archive.source_signature,
            "created_at": archive.created_at,
            "updated_at": archive.updated_at,
        }

        if archive.status == ProductDownloadArchiveStatus.READY:
            data["download_url"] = ProductDownloadArchiveService.build_download_url(
                archive,
                request.user,
                request,
            )
            data["expired_time"] = (
                ProductDownloadArchiveService.get_archive_expired_time(archive)
            )

        if archive.status == ProductDownloadArchiveStatus.FAILED:
            data["error_message"] = archive.error_message

        return data

    def __get_current_download_signature(self, product):
        product_path = pathlib.Path(settings.MEDIA_ROOT, product.path)
        return ProductDownloadArchiveService.build_source_signature(product_path)

    @action(methods=["POST"], detail=True, url_path="download/prepare")
    def download_prepare(self, request, **kwargs):
        product = self.get_object()
        source_signature = self.__get_current_download_signature(product)
        archive = ProductDownloadArchiveService.find_current_archive(
            product,
            source_signature,
        )

        if archive and archive.status in (
            ProductDownloadArchiveStatus.PENDING,
            ProductDownloadArchiveStatus.RUNNING,
            ProductDownloadArchiveStatus.READY,
        ):
            logger.info(
                "download_prepare reusing archive_id=%s task_id=%s product_id=%s status=%s",
                archive.pk,
                archive.task_id,
                product.pk,
                archive.status,
            )
            response_status = (
                status.HTTP_200_OK
                if archive.status == ProductDownloadArchiveStatus.READY
                else status.HTTP_202_ACCEPTED
            )
            return Response(
                self.__serialize_download_archive(archive, request),
                status=response_status,
            )

        archive = ProductDownloadArchive.objects.create(
            product=product,
            created_by=request.user,
            filename=f"{product.internal_name}.zip",
            source_signature=source_signature,
        )
        task = build_product_download_archive.delay(archive.pk)
        archive.task_id = task.id
        archive.save(update_fields=["task_id", "updated_at"])
        logger.info(
            "download_prepare queued archive_id=%s task_id=%s product_id=%s source_signature=%s",
            archive.pk,
            archive.task_id,
            product.pk,
            source_signature,
        )
        archive = ProductDownloadArchiveService.wait_for_archive_preparation(archive)
        response_status = (
            status.HTTP_200_OK
            if archive.status == ProductDownloadArchiveStatus.READY
            else status.HTTP_202_ACCEPTED
        )

        return Response(
            self.__serialize_download_archive(archive, request),
            status=response_status,
        )

    @action(methods=["GET"], detail=True, url_path="download/status")
    def download_status(self, request, **kwargs):
        product = self.get_object()
        source_signature = self.__get_current_download_signature(product)
        archive = ProductDownloadArchiveService.find_current_archive(
            product,
            source_signature,
        )

        if not archive:
            return Response(
                {"status": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(self.__serialize_download_archive(archive, request))

    @action(
        methods=["GET"],
        detail=True,
        url_path="download/file",
    )
    def download_file(self, request, **kwargs):
        product = self.get_object()
        token = request.GET.get("token")
        if not token:
            raise exceptions.PermissionDenied("Missing download token.")

        try:
            payload = ProductDownloadArchiveService.load_download_token(token)
        except signing.SignatureExpired:
            raise exceptions.PermissionDenied("Download token has expired.")
        except signing.BadSignature:
            raise exceptions.PermissionDenied("Invalid download token.")

        if str(payload.get("product_id")) != str(product.pk):
            raise exceptions.PermissionDenied("Invalid download token.")

        try:
            archive = ProductDownloadArchive.objects.select_related("product").get(
                pk=payload.get("archive_id"),
                product_id=product.pk,
                status=ProductDownloadArchiveStatus.READY,
            )
        except ProductDownloadArchive.DoesNotExist:
            return Response(
                {"error": "Download archive not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        archive_path = ProductDownloadArchiveService.get_archive_file_path(archive)
        if not archive_path.exists():
            return Response(
                {"error": "Download archive file not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        mimetype, _ = mimetypes.guess_type(archive_path)
        response = HttpResponse(content_type=mimetype)
        response["X-Accel-Redirect"] = (
            ProductDownloadArchiveService.get_archive_internal_redirect_path(archive)
        )
        response["Content-Length"] = archive_path.stat().st_size
        response["Content-Disposition"] = "attachment; filename={}".format(
            archive.filename
        )
        return response

    @action(methods=["GET"], detail=True)
    def download(self, request, **kwargs):
        """Download product"""
        try:
            product = self.get_object()
            product_path = pathlib.Path(settings.MEDIA_ROOT, product.path)
            product_metadata = loads(dumps(self.__get_full_product(product)))

            with tempfile.TemporaryDirectory() as tmpdirname:
                # Cria um arquivo zip no diretório tmp com os arquivos do produto
                zip_file = ProductDownloadArchiveService.build_zip(
                    product.internal_name, product_path, product_metadata, tmpdirname
                )

                # Abre o arquivo e envia em bites para o navegador
                mimetype, _ = mimetypes.guess_type(zip_file)
                size = zip_file.stat().st_size
                name = zip_file.name

                file_handle = open(zip_file, "rb")
                response = FileResponse(file_handle, content_type=mimetype)
                response["Content-Length"] = size
                response["Content-Disposition"] = "attachment; filename={}".format(name)
                response["Deprecation"] = "true"
                response["Link"] = (
                    f"</api/products/{product.pk}/download/prepare/>; "
                    'rel="successor-version"'
                )
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
            if main_file.storage_kind == FileStorageKind.HATS_COLLECTION:
                with tempfile.TemporaryDirectory() as tmpdirname:
                    zip_file = self.zip_directory(
                        main_file_path, product.internal_name, tmpdirname
                    )
                    size = zip_file.stat().st_size
                    file_handle = open(zip_file, "rb")
                    response = FileResponse(file_handle, content_type="application/zip")
                    response["Content-Length"] = size
                    response["Content-Disposition"] = (
                        f"attachment; filename={zip_file.name}"
                    )
                    return response

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
        if product_file.storage_kind == FileStorageKind.HATS_COLLECTION:
            content = {"message": "Table preview is not available for HATS products."}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        preview_path = RegistryProduct.get_table_preview_path(product)

        try:
            if preview_path.exists():
                try:
                    preview_payload = loads(preview_path.read_text(encoding="utf-8"))
                    records = preview_payload.get("results", [])
                    columns = preview_payload.get("columns", [])
                    count = int(preview_payload.get("count", len(records)))
                except Exception:
                    preview_path.unlink(missing_ok=True)
            else:
                records = None

            if not preview_path.exists():
                if RegistryProduct.is_table_preview_processing(product):
                    return Response(
                        {"message": self.TABLE_PREVIEW_PROCESSING_MESSAGE},
                        status=status.HTTP_202_ACCEPTED,
                    )

                started = RegistryProduct.start_table_preview_processing(product)
                if started:
                    try:
                        build_product_table_preview.delay(product.pk)
                    except Exception:
                        RegistryProduct.stop_table_preview_processing(product)
                        raise

                return Response(
                    {"message": self.TABLE_PREVIEW_PROCESSING_MESSAGE},
                    status=status.HTTP_202_ACCEPTED,
                )

            if records is None:
                preview_payload = loads(preview_path.read_text(encoding="utf-8"))
                records = preview_payload.get("results", [])
                columns = preview_payload.get("columns", [])
                count = int(preview_payload.get("count", len(records)))

            paginator = Paginator(records, page_size)
            records = paginator.get_page(page)

            return Response(
                {
                    "count": count,
                    "columns": columns,
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
            if product_file.storage_kind == FileStorageKind.HATS_COLLECTION:
                data = self.get_serializer(instance=product).data
                data["main_file"] = {
                    "name": product_file.name,
                    "type": product_file.type,
                    "extension": product_file.extension,
                    "size": product_file.size,
                    "n_rows": product_file.n_rows,
                    "storage_kind": product_file.storage_kind,
                    "metadata": product_file.metadata,
                }
                product_contents = self.__get_product_contents(product)
                if product_contents:
                    data["main_file"]["associated_columns"] = product_contents
                return Response(data)

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

            product_contents = self.__get_product_contents(product)
            if product_contents:
                main_file["associated_columns"] = product_contents

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
        return self.zip_directory(product_path, internal_name, tmpdir)

    def zip_directory(self, directory, internal_name, tmpdir):

        directory = pathlib.Path(directory)
        thash = "".join(secrets.choice(secrets.token_hex(16)) for i in range(5))
        zip_name = f"{internal_name}_{thash}.zip"
        zip_path = pathlib.Path(tmpdir, zip_name)

        with zipfile.ZipFile(
            zip_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as ziphandle:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    origin_file = os.path.join(root, file)
                    arcname = pathlib.Path(origin_file).relative_to(directory)
                    ziphandle.write(origin_file, arcname=arcname)

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

        is_specz = instance.product_type.name == "redshift_catalog"
        is_object = instance.product_type.name == "object_catalog"
        is_train = instance.product_type.name == "training_set"

        logger.debug("Status: %s", prodstatus)
        logger.debug("IsPubl: %s", is_published)

        check_prod = None

        if is_published:
            if is_specz and prodstatus:
                check_prod = self.__check_mandatory_columns(
                    instance, ["Dec", "RA", "z"]
                )
            elif is_object and prodstatus:
                check_prod = self.__check_mandatory_columns(instance, ["Dec", "RA"])
            elif is_train and prodstatus:
                check_prod = self.__check_mandatory_columns(instance, ["z"])

        if check_prod and not check_prod.get("success", False):
            content = check_prod.get("message")
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        return super(ProductViewSet, self).partial_update(request, *args, **kwargs)

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
