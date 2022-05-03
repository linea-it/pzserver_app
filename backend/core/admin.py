from django.contrib import admin
from core.models import ProductType, Product, Release


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_name", "created_at")

    search_fields = ("name", "display_name")


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_name", "created_at")

    search_fields = ("name", "display_name")


@admin.register(Product)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_type",
        "release",
        "user",
        "display_name",
        "official_product",
        "survey",
        "pz_code",
        "created_at",
    )

    search_fields = ("name", "display_name")
