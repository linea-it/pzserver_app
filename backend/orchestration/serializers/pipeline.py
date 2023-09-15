from core.models import ProductType
from orchestration.models import Pipeline
from orchestration.utils import get_pipeline_config, get_pipeline_version
from rest_framework import serializers


class PipelineSerializer(serializers.ModelSerializer):
    product_types = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), many=True
    )

    class Meta:
        model = Pipeline
        read_only_fields = (
            "display_name",
            "created_at",
        )
        exclude = ["description"]


class PipelineDetailSerializer(PipelineSerializer):
    config = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()

    def get_config(self, obj):
        return get_pipeline_config(obj.name)

    def get_version(self, obj):
        return get_pipeline_version(obj.name)


class PipelineSimpleSerializer(PipelineDetailSerializer):
    
    class Meta:
        model = Pipeline
        fields = ("id", "name", "display_name", "version")
