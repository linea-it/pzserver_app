from core.models import ProductType
from django.db import models


class Pipeline(models.Model):

    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    version = models.CharField(max_length=55)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    system_config = models.JSONField(null=True, blank=True)
    product_types_accepted= models.ManyToManyField(
        ProductType, related_name="pipelines"
    )
    output_product_type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE,
        related_name="output_product_type",
    )

    def __str__(self):
        return f"{self.display_name}"
    