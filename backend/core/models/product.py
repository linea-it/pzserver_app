import logging

from core.models import ProductType, Release
from django.contrib.auth.models import User
from django.db import models


def upload_product_files(instance, filename):
    return f"tmp/{instance.internal_name}/{filename}"


class ProductStatus(models.IntegerChoices):
    REGISTERING = 0, "Registering"
    REGISTERED = 1, "Registered"
    PUBLISHED = 2, "Published"


class Product(models.Model):

    product_type = models.ForeignKey(
        ProductType, on_delete=models.CASCADE, related_name="products"
    )
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        default=None,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    internal_name = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    display_name = models.CharField(max_length=255)
    # main_file = models.FileField(
    #     upload_to=upload_product_files, null=False, blank=False
    # )
    file_name = models.CharField(max_length=120, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    file_extension = models.CharField(max_length=10, null=True, blank=True)
    # description_file = models.FileField(
    #     upload_to=upload_product_files, null=True, blank=True
    # )
    official_product = models.BooleanField(default=False)
    survey = models.CharField(max_length=255, null=True, blank=True)
    pz_code = models.CharField(max_length=55, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        verbose_name="Status",
        default=ProductStatus.REGISTERING,
        choices=ProductStatus.choices,
    )

    def __str__(self):
        return f"{self.display_name}"
