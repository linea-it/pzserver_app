from rest_framework import serializers
from core.models import ProductFile, Product


class ProductFileSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=False
    )

    file = serializers.FileField()

    class Meta:
        model = ProductFile
        read_only_fields = (
            "name",
            "size",
            "extension",
        )
        fields = "__all__"
