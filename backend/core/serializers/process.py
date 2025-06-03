from core.models import Process, Release
from core.serializers.product import ProductSerializer
from rest_framework import serializers


class ProcessSerializer(serializers.ModelSerializer):

    release = serializers.PrimaryKeyRelatedField(
        queryset=Release.objects.all(), many=False, allow_null=True, required=False
    )
    release_name = serializers.SerializerMethodField()
    pipeline_name = serializers.SerializerMethodField()
    pipeline_version = serializers.SerializerMethodField()
    owned_by = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    provenance_inputs = ProductSerializer(source="inputs", many=True, read_only=True)

    class Meta:
        model = Process
        read_only_fields = (
            "pipeline_version",
            "is_owner",
            "upload",
            "status",
            "orchestration_process_id",
            "started_at",
            "ended_at",
            "path",
            "provenance_inputs",
        )
        exclude = ("user", "task_id")

    def get_pipeline_name(self, obj):
        return obj.pipeline.name

    def get_pipeline_version(self, obj):
        return obj.pipeline.version

    def get_release_name(self, obj):
        try:
            return obj.release.display_name
        except:
            return None

    def get_owned_by(self, obj):
        return obj.user.username

    def get_is_owner(self, obj):
        current_user = self.context["request"].user
        if obj.user.pk == current_user.pk:
            return True
        else:
            return False
