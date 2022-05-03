from rest_framework import serializers
from core.models import ProductType, Release, Product


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = "__all__"


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Release
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):

    release = serializers.PrimaryKeyRelatedField(
        queryset=Release.objects.all(), many=False
    )
    release_name = serializers.SerializerMethodField()

    product_type = serializers.PrimaryKeyRelatedField(
        queryset=ProductType.objects.all(), many=False
    )
    product_type_name = serializers.SerializerMethodField()

    uploaded_by = serializers.SerializerMethodField()

    class Meta:
        model = Product
        read_only_fields = (
            "file_size",
            "file_extension",
            "file_name",
        )
        exclude = ["user"]

    def get_product_type_name(self, obj):
        try:
            return obj.product_type.display_name
        except:
            return None

    def get_release_name(self, obj):
        try:
            return obj.release.display_name
        except:
            return None

    def get_uploaded_by(self, obj):
        try:
            return obj.user.username
        except:
            return None
