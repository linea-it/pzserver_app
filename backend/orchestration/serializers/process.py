from core.models import Product
from orchestration.models import Pipeline, Process
from orchestration.serializers import PipelineSimpleSerializer
from rest_framework import serializers


class ProcessSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    pipeline_name = serializers.SerializerMethodField()
    inputs = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True
    )
    deph = 1

    class Meta:
        model = Process
        read_only_fields = (
            "pipeline_version",
            "started_at",
            "ended_at",
            "status",
            "user",
            "task_id",
            "comment",
        )
        exclude = ["path"]

    def get_owner(self, obj):
        return obj.user.username

    def get_pipeline_name(self, obj):
        return obj.pipeline.name