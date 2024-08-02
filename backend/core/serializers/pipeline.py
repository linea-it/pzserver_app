from core.models import Pipeline
from rest_framework import serializers


class PipelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pipeline
        fields = "__all__"
