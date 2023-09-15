from django.db import transaction
from orchestration.models import Pipeline
from orchestration.serializers import (PipelineDetailSerializer,
                                       PipelineSerializer)
from orchestration.utils import get_pipeline, get_pipeline_config
from rest_framework import status, viewsets
from rest_framework.response import Response


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    search_fields = ["name", "display_name"]
    ordering_fields = [
        "id",
        "name",
        "display_name",
        "created_at",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PipelineDetailSerializer
        return PipelineSerializer

    def create(self, request):
        if not request.user.profile.is_admin():
            content = {"error": "User is not admin"}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        pipeline_name = request.data["name"]

        # WARN: the pipeline must be installed and tested in the infra
        # before registering in the database
        try:
            # gets pipeline information from $PIPELINES_DIR
            pipeline_system = get_pipeline(pipeline_name)
        except Exception as err:
            content = {
                "error": str(err),
                "detail": f"Pipeline {pipeline_name} not instaled",
            }
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = self.get_serializer(data=request.data)

        try:
            with transaction.atomic():
                serializer.is_valid(raise_exception=True)
                instance = serializer.save()
                pipeline = Pipeline.objects.get(pk=instance.pk)
                pipeline.display_name = pipeline_system.get("dname", None)
                pipeline.save()

                data = self.get_serializer(instance=pipeline).data
                return Response(data, status=status.HTTP_201_CREATED)
        except Exception as err:
            content = {"error": str(err), "detail": ""}
            return Response(content, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
