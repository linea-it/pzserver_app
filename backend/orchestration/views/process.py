import pathlib

from django.conf import settings
from django.db import transaction
from orchestration.filters import ProcessFilter
from orchestration.models import Process
from orchestration.serializers import ProcessSerializer
from orchestration.utils import get_pipeline_version
from rest_framework import exceptions, status, viewsets
from rest_framework.response import Response


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    search_fields = [
        "pipeline__name",
        "pipeline__display_name",
        "user__username",
        "user__first_name",
        "user__last_name",
    ]
    filterset_class = ProcessFilter
    ordering_fields = [
        "id",
        "status",
        "created_at",
        "started_at",
        "ended_at",
    ]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        try:
            with transaction.atomic():
                serializer.is_valid(raise_exception=True)
                instance = self.perform_create(serializer)
                process = Process.objects.get(pk=instance.pk)

                # fill the current pipeline version
                process.pipeline_version = get_pipeline_version(process.pipeline.name)

                # create process path
                process.path = str(instance.pk).zfill(8)
                path = pathlib.Path(settings.PROCESSING_DIR, process.path)
                path.mkdir(parents=True, exist_ok=True)

                process.save()

                data = self.get_serializer(instance=process).data
                return Response(data, status=status.HTTP_201_CREATED)
        except Exception as e:
            content = {"error": str(e)}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, pk=None, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.user.pk:
            return super(ProcessViewSet, self).destroy(request, pk, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied()
