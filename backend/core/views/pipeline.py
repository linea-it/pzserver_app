from core import models
from core.serializers import PipelineSerializer
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class PipelineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Pipeline.objects.all()
    serializer_class = PipelineSerializer
    filterset_fields = [
        "id",
        "name",
    ]
    search_fields = [
        "display_name",
        "description",
    ]
    ordering = ["-created_at"]

    @action(methods=["GET"], detail=True)
    def api_schema(self, request):
        meta = self.metadata_class()
        data = meta.determine_metadata(request, self)
        return Response(data)
    