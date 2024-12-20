import os

from core.models import Product
from django.db import models


def upload_product_files(instance, filename):
    return f"{instance.product.path}/{filename}"


class FileRoles(models.IntegerChoices):
    MAIN = 0, "Main"
    DESCRIPTION = 1, "Description"
    AUXILIARY = 2, "Auxiliary"


class ProductFile(models.Model):

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="files")

    file = models.FileField(upload_to=upload_product_files)

    role = models.IntegerField(
        verbose_name="Role",
        default=FileRoles.MAIN,
        choices=FileRoles.choices,
    )

    name = models.CharField(verbose_name="Name", max_length=1024, null=True, blank=True)
    type = models.CharField(
        verbose_name="Mime Type", max_length=128, null=True, blank=True
    )
    n_rows = models.IntegerField(verbose_name="Number of rows", null=True, blank=True)
    size = models.IntegerField(verbose_name="Size", null=True, blank=True)
    extension = models.CharField(
        verbose_name="Extension", max_length=10, null=True, blank=True
    )
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.display_name} - {os.path.basename(self.file.name)}"

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete()
        super().delete(*args, **kwargs)
