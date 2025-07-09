import json
import logging
import pathlib

import requests
from core.maestro import Maestro
from core.models import Pipeline, Process, ProductStatus
from core.product_steps import CreateProduct
from core.serializers import ProcessSerializer
from core.utils import format_query_to_char
from django.conf import settings
from django_filters import rest_framework as filters
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

LOGGER = logging.getLogger("django")


class ProcessFilter(filters.FilterSet):
    release__isnull = filters.BooleanFilter(field_name="release", lookup_expr="isnull")
    pipeline__or = filters.CharFilter(method="filter_pipeline")
    pipeline = filters.CharFilter(method="filter_pipeline")
    release_name__or = filters.CharFilter(method="filter_release")
    release_name = filters.CharFilter(method="filter_release")

    class Meta:
        model = Process
        fields = [
            "pipeline",
            "status",
            "release",
            "upload",
            "user",
        ]

    def filter_user(self, queryset, name, value):
        query = format_query_to_char(
            name, value, ["user__username", "user__first_name", "user__last_name"]
        )

        return queryset.filter(query)

    def filter_pipeline(self, queryset, name, value):
        query = format_query_to_char(
            name, value, ["pipeline__display_name", "pipeline__name"]
        )

        return queryset.filter(query)

    def filter_release(self, queryset, name, value):
        query = format_query_to_char(name, value, ["release__display_name"])
        return queryset.filter(query)


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    search_fields = [
        "pipeline_name",
        "pipeline_display_name",
        "upload",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]
    filterset_class = ProcessFilter
    ordering_fields = [
        "id",
        "created_at",
    ]
    ordering = ["-created_at"]

    def create(self, request):
        try:
            LOGGER.debug("Instantiating maestro: %s", settings.ORCHEST_URL)
            maestro = Maestro(url=settings.ORCHEST_URL)
        except requests.exceptions.ConnectionError as err:
            content = {
                "error": (
                    "The service is not responding. "
                    "Please contact helpdesk@linea.org.br to receive user support."
                )
            }
            LOGGER.error(err)
            return Response(content, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except Exception as err:
            content = {"error": str(err)}
            LOGGER.error(err)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        LOGGER.debug(f"Create process: {request.data}")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            LOGGER.debug("Create DB process: %s", request.data)
            instance = self.perform_create(serializer)
            process = Process.objects.get(pk=instance.pk)
            process.save()
            LOGGER.debug("Process ID %s inserted.", instance.pk)
        except Exception as err:
            content = {"error": str(err)}
            LOGGER.error(err)
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            if process.used_config:
                used_config = process.used_config

            used_config["inputs"] = {}

            if process.release:
                release_path = pathlib.Path(settings.DATASETS_DIR, process.release.name)

                LOGGER.debug("Used release: %s", process.release)

                if not release_path.is_dir() and not release_path.is_symlink():
                    raise ValueError(f"Release path not found: {str(release_path)}")

                used_config["inputs"]["dataset"] = {
                    "path": str(release_path),
                    "columns": {"id": process.release.indexing_column},
                }

            LOGGER.debug("Used configuration: %s", used_config)

            _inputs = process.inputs.all()
            inputfiles = []

            for _input in _inputs:
                main_file = _input.files.get(role=0)
                filepath = pathlib.Path(
                    settings.UPLOAD_DIR, _input.path, main_file.name
                )

                if not filepath.is_file():
                    raise FileNotFoundError(f"file not found: {str(filepath)}")

                ra = self.__get_mapped_column(_input, "RA")
                dec = self.__get_mapped_column(_input, "Dec")
                z = self.__get_mapped_column(_input, "z")
                _id = self.__get_mapped_column(_input, "id")
                z_flag = self.__get_mapped_column(_input, "z_flag")
                z_err = self.__get_mapped_column(_input, "z_err")
                survey = self.__get_mapped_column(_input, "survey")

                ext = main_file.extension

                _file = {
                    "path": str(filepath),
                    "format": ext.replace(".", ""),
                    "columns": {
                        "ra": ra,
                        "dec": dec,
                        "z": z,
                        "id": _id,
                        "z_flag": z_flag,
                        "z_err": z_err,
                        "survey": survey,
                    },
                    "internal_name": _input.internal_name,
                }
                inputfiles.append(_file)

            used_config["inputs"]["specz"] = inputfiles

            output_format = request.data.get("output_format", None)
            if output_format and output_format != "specz":
                used_config["output_format"] = output_format

            used_config["output_dir"] = str(process.upload.path)
            used_config["output_root_dir"] = settings.UPLOAD_DIR

            LOGGER.debug("Used config: %s", used_config)

            orch_process = maestro.start(
                pipeline=process.pipeline.name, config=used_config
            )

            orch_process_id = orch_process.get("id")

            LOGGER.debug("Process submitted: OrchID %s", orch_process_id)

            process.orchestration_process_id = orch_process_id
            process.used_config = json.loads(orch_process.get("used_config", None))
            process.path = orch_process.get("path_str")
            process.save()

            data = self.get_serializer(instance=process).data
            return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            msg = f"Orchestration API failure: {str(e)}"
            LOGGER.error(msg)
            content = {"error": msg}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def __get_mapped_column(self, product, column):
        """Get mapped column by column name

        Args:
            product (Product): Product object
            column (str): column name
        """

        columns = product.contents.filter(alias=column)

        if columns.count() != 1:
            LOGGER.warning(f"Column {column} was not mapped for product {product}.")
            LOGGER.warning(f"Column {column}: value {column.lower()} will be used.")
            if column.lower() in ("ra", "dec", "z"):
                value = column.lower()
            else:
                value = None
        else:
            obj = columns[0]
            value = obj.column_name

        return value

    def perform_create(self, serializer):
        """Add user and upload"""

        owned_by = self.request.user
        upload = self.create_initial_upload(serializer, owned_by)
        return serializer.save(user=owned_by, upload=upload)

    def create_initial_upload(self, serializer, user):
        """Creates the upload with initial data before starting processing."""

        data = serializer.initial_data
        pipeline = Pipeline.objects.get(pk=data.get("pipeline"))
        upload_data = {
            "display_name": data.get("display_name"),
            "release": data.get("release", None),
            "pz_code": data.get("pz_code", None),
            "official_product": data.get("official_product", False),
            "description": data.get("description", None),
            "product_type": pipeline.output_product_type.pk,  # type: ignore
        }
        product = CreateProduct(upload_data, user)
        check_prodtype = product.check_product_types()

        if not check_prodtype.get("success"):
            raise ValueError(check_prodtype.get("message"))

        product.status = ProductStatus.PROCESSING  # type: ignore
        product.save()
        return product.data

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)

    @action(methods=["GET"], detail=True)
    def stop(self, request, *args, **kwargs):
        """Stop process"""

        try:
            instance = self.get_object()
            _id = instance.pk
            process = Process.objects.get(pk=_id)
            orchestration_process_id = process.orchestration_process_id

            if not orchestration_process_id:
                raise ValueError(f"Process[{_id}]: orchestration process not found.")

            maestro = Maestro(url=settings.ORCHEST_URL)
            maestro.stop(orchestration_process_id)
            orcdata = maestro.status(orchestration_process_id)
            process.status = orcdata.get("status", "Stopping*")
            process.save()
            data = self.get_serializer(instance=process).data
            code_status = status.HTTP_200_OK
        except Exception as err:
            data = {"error": str(err)}
            code_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        LOGGER.info("Process[%s]: %s", str(process), data)
        return Response(data, status=code_status)

    def destroy(self, request, pk=None, *args, **kwargs):
        """Product can only be deleted by the OWNER or if the user
        has an admin profile.
        """

        instance = self.get_object()
        if instance.can_delete(self.request.user):
            return super(ProcessViewSet, self).destroy(request, pk, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied()
