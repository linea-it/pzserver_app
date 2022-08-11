import logging

from core.models import ProductType, Release
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
import pathlib
import shutil
import logging


def upload_product_files(instance, filename):
    return f"{instance.product_type.name}/{instance.internal_name}/{filename}"


class ProductStatus(models.IntegerChoices):
    REGISTERING = 0, "Registering"
    PUBLISHED = 1, "Published"
    FAILED = 9, "Failed"


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

    def delete(self, *args, **kwargs):
        # Antes de remover o registro verifica se existe
        # diretório, se houver remove.
        # OBS não é executado pelo admin
        product_path = pathlib.Path(
            settings.MEDIA_ROOT, f"{self.product_type.name}/{self.internal_name}"
        )
        if product_path.exists():
            try:
                shutil.rmtree(product_path)
            except OSError as e:
                raise Exception("Error: %s : %s" % (product_path, e.strerror))

        super().delete(*args, **kwargs)
