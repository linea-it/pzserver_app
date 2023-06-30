from core.models import Product, ProductType, Release
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

    uploaded_by = serializers.SerializerMethodField()

    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Product
        read_only_fields = ("internal_name", "is_owner")
        exclude = ["user", "path"]

    def get_product_type_name(self, obj):
        return obj.product_type.display_name

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
        

class ProductSimpleSerializer(ProductSerializer):
    
    class Meta:
        model = Product
        fields = ("id", "display_name", "internal_name")

