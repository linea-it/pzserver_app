import logging
import pathlib
import shutil

from core.models import ProductType, Release
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

# def upload_product_files(instance, filename):
#     return f"{instance.product_type.name}/{instance.internal_name}/{filename}"


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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products")
    internal_name = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    display_name = models.CharField(max_length=255)
    official_product = models.BooleanField(default=False)
    pz_code = models.CharField(max_length=55, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.IntegerField(
        verbose_name="Status",
        default=ProductStatus.REGISTERING,
        choices=ProductStatus.choices,
    )
    path = models.FilePathField(
        verbose_name="Path", null=True, blank=True, default=None
    )

    def __str__(self):
        return f"{self.display_name}"

    def delete(self, *args, **kwargs):
        # Antes de remover o registro verifica se existe
        # diretório, se houver remove.
        # OBS não é executado pelo admin
        product_path = pathlib.Path(settings.MEDIA_ROOT, self.path)
        if product_path.exists():
            # TODO: mover esta exception para uma funcao separada para que possa ser executado o test.
            # try:
            shutil.rmtree(product_path)
            # except OSError as e:
            # raise OSError("Failed to remove directory: [ %s ] %s" % (product_path, e))

        super().delete(*args, **kwargs)

    def can_delete(self, user) -> bool:
        if self.user.id == user.id or user.profile.is_admin():
            return True
        return False

    def can_update(self, user) -> bool:
        if self.user.id == user.id or user.profile.is_admin():
            return True
        return False
    