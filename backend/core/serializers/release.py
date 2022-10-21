from rest_framework import serializers
from core.models import Release


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = "__all__"
