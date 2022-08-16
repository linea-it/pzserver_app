from rest_framework import serializers
from core.models import ProductContent, Product


class ProductContentSerializer(serializers.ModelSerializer):

    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=False
    )

    class Meta:
        model = ProductContent
        fields = "__all__"
