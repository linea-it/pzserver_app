from rest_framework import serializers
from core.models import Release


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = "__all__"


class ReleaseHatsConfigSerializer(serializers.Serializer):
    release = serializers.CharField()
    last_modified = serializers.DateTimeField()
    config = serializers.JSONField()
