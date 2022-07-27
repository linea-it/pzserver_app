from core.models import Product
from django.db import models


class ProductContent(models.Model):

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="contents"
    )

    column_name = models.CharField(max_length=256, verbose_name="Column Name")

    ucd = models.CharField(
        max_length=128,
        verbose_name="UCD",
        help_text="The standard unified content descriptor.",
        null=True,
        blank=True,
        default=None,
    )

    order = models.IntegerField(
        verbose_name="Order",
        help_text="Order of columns in the product.",
        null=True,
        blank=True,
        default=0,
    )

    def __str__(self):
        return f"{self.product.display_name} - {self.column_name}"
