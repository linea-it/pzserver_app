from django.db import models


class ProductType(models.Model):
    name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    order = models.IntegerField(null=True, blank=True, default=None)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.display_name}"
