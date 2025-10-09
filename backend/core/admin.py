from core.models import (
    GroupMetadata,
    Pipeline,
    Process,
    Product,
    ProductContent,
    ProductFile,
    ProductType,
    Release,
)
from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("id", "pipeline", "status", "user", "created_at")
    exclude = ["path"]
    search_fields = ("pipeline", "status")


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_name", "created_at")
    search_fields = ("name", "display_name")


@admin.register(Release)
class ReleaseAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "display_name", "is_public", "created_at")
    list_filter = ("is_public", "created_at")
    filter_horizontal = ("access_groups",)
    search_fields = ("name", "display_name")

    fieldsets = (
        (None, {"fields": ("name", "display_name", "description", "indexing_column")}),
        (
            "Data Configuration",
            {"fields": ("has_mag_hats", "has_flux_hats", "dereddening", "fluxes")},
        ),
        ("Access Control", {"fields": ("is_public", "access_groups")}),
    )


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
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
        "updated_at",
        "status",
    )

    search_fields = ("internal_name", "display_name")

    form = ProductAdminForm

    # This will help you to disbale add functionality
    def has_add_permission(self, request):
        return False


@admin.register(ProductContent)
class ProductContentAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "column_name", "ucd", "alias", "order")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProductFile)
class ProductFileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "product",
        "file",
        "role",
        "type",
        "size",
        "n_rows",
        "extension",
        "created",
        "updated",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CustomUserAdmin(UserAdmin):
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


@admin.register(GroupMetadata)
class GroupMetadataAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "source", "display_name", "last_sync")
    list_filter = ("source", "last_sync")
    search_fields = ("group__name", "display_name", "description")
    readonly_fields = ("created_at", "updated_at", "last_sync")

    fieldsets = (
        (None, {"fields": ("group", "source", "display_name", "description")}),
        ("LIneA Info", {"fields": ("last_sync",), "classes": ("collapse",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
