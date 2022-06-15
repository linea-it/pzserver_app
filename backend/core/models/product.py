import logging

from core.models import ProductType, Release
from django.contrib.auth.models import User
from django.db import models


def upload_product_files(instance, filename):
    # log = logging.getLogger("registry_product")
    # log.info("Model Upload to")
    # release_name = instance.release.name
    # product_type = instance.product_type.name
    # log.debug("Release Name: %s" % release_name)
    # log.debug("Product Type: %s" % product_type)

    return f"tmp/{instance.internal_name}/{filename}"


class Product(models.Model):

    product_type = models.ForeignKey(
        ProductType, on_delete=models.PROTECT, related_name="products"
    )
    release = models.ForeignKey(
        Release,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="products")
    internal_name = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    display_name = models.CharField(max_length=255)
    main_file = models.FileField(
        upload_to=upload_product_files, null=False, blank=False
    )
    file_name = models.CharField(max_length=120, null=True, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    file_extension = models.CharField(max_length=10, null=True, blank=True)
    description_file = models.FileField(
        upload_to=upload_product_files, null=True, blank=True
    )
    official_product = models.BooleanField(default=False)
    survey = models.CharField(max_length=255, null=True, blank=True)
    pz_code = models.CharField(max_length=55, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.display_name}"
