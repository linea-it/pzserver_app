from core.models import Product, ProductFile
from rest_framework import serializers


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
            "n_rows",
            "extension",
        )
        fields = "__all__"
