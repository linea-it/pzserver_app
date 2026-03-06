import logging

import requests
from core.maestro import Maestro
from core.models import Process
from core.process.builders.upload_builder import UploadBuilder
from core.process.service import ProcessService
from core.serializers import ProcessSerializer
from core.utils import format_query_to_char, get_logs
from django_filters import rest_framework as filters
from rest_framework import exceptions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
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
    parser_classes = (MultiPartParser, FormParser, JSONParser)

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        upload = UploadBuilder(serializer, request.user).build()
        process = serializer.save(user=request.user, upload=upload)

        try:
            ProcessService(request, process).submit()
        except Exception as err:
            LOGGER.error(err)
            return Response(
                {"error": str(err)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            self.get_serializer(instance=process).data, status=status.HTTP_201_CREATED
        )

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):

        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)

        return Response(data)

    @action(methods=["GET"], detail=True)
    def logs(self, request, *args, **kwargs):
        """Retrieve logs for a process"""

        process = self.get_object()

        try:
            logs = get_logs(process.path, process.upload.path)
            return Response(logs)
        except Exception as err:
            LOGGER.error(err)
            return Response(
                {"error": str(err)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(methods=["GET"], detail=True)
    def stop(self, request, *args, **kwargs):
        """Stop process"""

        process = self.get_object()

        try:
            process = ProcessService(request, process).stop()
            data = self.get_serializer(process).data
            return Response(data)
        except Exception as err:
            LOGGER.error(err)
            return Response(
                {"error": str(err)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def destroy(self, request, pk=None, *args, **kwargs):
        """Product can only be deleted by the OWNER or admin"""

        instance = self.get_object()

        if not instance.can_delete(request.user):
            raise exceptions.PermissionDenied()

        return super().destroy(request, pk, *args, **kwargs)
