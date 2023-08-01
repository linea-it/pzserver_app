from core.models import (Product, ProductContent, ProductFile, ProductType,
                         Profile, Release)
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_name", "created_at")

    search_fields = ("name", "display_name")


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_name", "created_at")

    search_fields = ("name", "display_name")


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ["path"]
        # widgets = {"path": forms.RadioSelect}
        # fields = "__all__"  # required for Django 3.x


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product_type",
        "release",
        "user",
        "internal_name",
        "display_name",
        "official_product",
        "pz_code",
        "created_at",
        "status",
    )

    search_fields = ("name", "display_name")

    form = ProductAdminForm

    # This will help you to disbale add functionality
    def has_add_permission(self, request):
        return False


@admin.register(ProductContent)
class ProductContentAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "column_name", "ucd", "alias", "order")

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "file", "role",
                    "type", "size", "extension")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = (
        "id",
        "username",
        "get_display_name",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "get_group",
    )
    readonly_fields = ("id",)
    list_select_related = ("profile",)

    def get_display_name(self, instance):
        return instance.profile.display_name

    get_display_name.short_description = "Display Name"

    def get_group(self, instance):
        groups = instance.groups.all()
        a_groups = []
        for group in groups:
            a_groups.append(group.name)

        return ", ".join(a_groups)

    get_group.short_description = "Groups"

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
