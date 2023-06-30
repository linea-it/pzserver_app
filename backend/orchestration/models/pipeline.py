from core.models import ProductType
from django.db import models


class Pipeline(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    use_release = models.BooleanField(default=False)
    product_types = models.ManyToManyField(ProductType, related_name="pipelines")

    def __str__(self):
        return f"{self.name}"
