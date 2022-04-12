from rest_framework import serializers
from core import models


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ProductType
        fields = "__all__"


class ReleaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Release
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = "__all__"
        read_only_fields = ("file_size", "file_extension", "file_name",)
