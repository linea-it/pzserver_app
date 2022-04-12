from django.contrib import admin
from core.models import ProductType, Product, Release

admin.site.register(ProductType)
admin.site.register(Release)
admin.site.register(Product)
