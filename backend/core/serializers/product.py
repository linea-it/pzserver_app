from core.models import Product, ProductStatus, ProductType, Release
from pkg_resources import require
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):

    release = serializers.PrimaryKeyRelatedField(
        queryset=Release.objects.all(), many=False, allow_null=True, required=False
    )

    release_name = serializers.SerializerMethodField()

    product_type = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), many=False
    )
    product_type_name = serializers.SerializerMethodField()

    product_type_internal_name = serializers.SerializerMethodField()

    uploaded_by = serializers.SerializerMethodField()

    is_owner = serializers.SerializerMethodField()

    origin = serializers.SerializerMethodField()

    process_status = serializers.SerializerMethodField()

    process_id = serializers.SerializerMethodField()

    product_status = serializers.SerializerMethodField()

    can_delete = serializers.SerializerMethodField()

    can_update = serializers.SerializerMethodField()

    class Meta:
        model = Product
        read_only_fields = (
            "internal_name",
            "is_owner",
            "origin",
            "process_status",
            "product_status",
        )
        exclude = ["user", "path"]

    def get_product_type_name(self, obj):
        return obj.product_type.display_name

    def get_product_type_internal_name(self, obj):
        return obj.product_type.name

    def get_release_name(self, obj):
        try:
            return obj.release.display_name
        except:
            return None

    def get_uploaded_by(self, obj):
        return obj.user.username

    def get_is_owner(self, obj):
        current_user = self.context["request"].user
        if obj.user.pk == current_user.pk:
            return True
        else:
            return False

    def get_origin(self, obj):
        return (
            obj.process.pipeline.display_name if hasattr(obj, "process") else "Upload"
        )

    def get_process_status(self, obj):
        return obj.process.status if hasattr(obj, "process") else None

    def get_process_id(self, obj):
        return obj.process.id if hasattr(obj, "process") else None

    def get_product_status(self, obj):
        pr = ProductStatus(obj.status)
        return pr.label

    def get_can_delete(self, obj):
        current_user = self.context["request"].user
        return obj.can_delete(current_user)

    def get_can_update(self, obj):
        current_user = self.context["request"].user
        return obj.can_update(current_user)
