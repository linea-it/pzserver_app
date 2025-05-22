from core.models import Product, ProductFile, FileRoles
from rest_framework import serializers


class ProductFileSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=False
    )

    file = serializers.FileField()

    can_delete = serializers.SerializerMethodField()

    role_name = serializers.SerializerMethodField()


    class Meta:
        model = ProductFile
        read_only_fields = (
            "name",
            "size",
            "n_rows",
            "extension",
        )
        fields = "__all__"

    def get_can_delete(self, obj):
        current_user = self.context["request"].user
        return obj.can_delete(current_user)

    def get_role_name(self, obj):
        pr = FileRoles(obj.role)
        return pr.label