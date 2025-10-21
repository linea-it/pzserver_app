from functools import wraps

from core.models import Product, Release
from core.services import AccessControlService
from django.core.exceptions import PermissionDenied
from django.http import Http404
from rest_framework.permissions import BasePermission


def require_access_to_release(view_func=None, *, release_param="release_id"):
    """
    Checks whether the user has access to the specified release.

    Args:
        view_func: View function to be decorated
        release_param: Parameter name containing the release ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Unauthenticated user: %s" % request.user)

            release_id = kwargs.get(release_param) or request.GET.get(release_param)
            if not release_id:
                return func(request, *args, **kwargs)

            try:
                release = Release.objects.get(id=release_id)
                if not AccessControlService.user_can_access_release(
                    request.user, release
                ):
                    raise PermissionDenied(
                        "User: %s - Access denied to release %s"
                        % (request.user, release)
                    )
            except Release.DoesNotExist:
                raise Http404("Release ID %s not found" % release_id)

            return func(request, *args, **kwargs)

        return wrapper

    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


def require_access_to_product(view_func=None, *, product_param="product_id"):
    """
    Checks whether the user has access to the specified product.

    Args:
        view_func: View function to be decorated
        product_param: Parameter name containing the product ID
    """

    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Unauthenticated user: %s" % request.user)

            product_id = kwargs.get(product_param) or request.GET.get(product_param)
            if not product_id:
                return func(request, *args, **kwargs)

            try:
                product = Product.objects.get(id=product_id)
                if not AccessControlService.user_can_access_product(
                    request.user, product
                ):
                    raise PermissionDenied(
                        "User: %s - Access denied to product %s"
                        % (request.user, product)
                    )
            except Product.DoesNotExist:
                raise Http404("Product ID %s not found" % product_id)

            return func(request, *args, **kwargs)

        return wrapper

    if view_func is None:
        return decorator
    else:
        return decorator(view_func)


class AccessControlMixin:
    """
    Mixin for views that need group-based access control.
    """

    def get_accessible_releases_queryset(self):
        """Returns queryset of releases accessible to the current user."""
        return AccessControlService.filter_accessible_releases(self.request.user)

    def get_accessible_products_queryset(self):
        """Returns queryset of products accessible to the current user."""
        return AccessControlService.filter_accessible_products(self.request.user)

    def check_release_access(self, release: Release):
        """
        Verifys if the current user has access to the release.
        Upraises PermissionDenied if access is not allowed.
        """
        if not AccessControlService.user_can_access_release(self.request.user, release):
            raise PermissionDenied(
                "User %s - Access denied to release %s" % (self.request.user, release)
            )

    def check_product_access(self, product: Product):
        """
        Verifys if the current user has access to the product.
        Upraises PermissionDenied if access is not allowed.
        """
        if not AccessControlService.user_can_access_product(self.request.user, product):
            raise PermissionDenied(
                "User %s - Access denied to product %s" % (self.request.user, product)
            )


class ReleaseAccessPermission(BasePermission):
    """
    Permission DRF to check access to releases.
    """

    def has_permission(self, request, view):
        """Checks if the user has basic permission (being authenticated)."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Checks if the user has access to the specific release object."""
        if isinstance(obj, Release):
            return AccessControlService.user_can_access_release(request.user, obj)
        return True


class ProductAccessPermission(BasePermission):
    """
    Permission DRF to check access to products based on associated release.
    """

    def has_permission(self, request, view):
        """Checks if the user has basic permission (being authenticated)."""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Checks if the user has access to the specific product object."""
        if isinstance(obj, Product):
            return AccessControlService.user_can_access_product(request.user, obj)
        return True


class GroupMembershipPermission(BasePermission):
    """
    Permission DRF to check if the user belongs to at least one of the required groups.
    """

    required_groups = []  # Lista de nomes de grupos necessários

    def has_permission(self, request, view):
        """Checks if the user belongs to at least one of the required groups."""
        if not request.user or not request.user.is_authenticated:
            return False

        if not self.required_groups:
            return True

        # Administrators always have access
        if request.user.profile.is_admin():
            return True

        user_groups = AccessControlService.get_user_groups(request.user)
        user_group_names = set(user_groups.values_list("name", flat=True))
        required_group_names = set(self.required_groups)

        return bool(user_group_names & required_group_names)


def user_in_groups(groups: list):
    """
    Checks whether the user belongs to at least one of the specified groups.

    Args:
        groups: group names required for access
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Unauthenticated user: %s" % request.user)

            # Administrators always have access
            if request.user.profile.is_admin():
                return view_func(request, *args, **kwargs)

            user_groups = AccessControlService.get_user_groups(request.user)
            user_group_names = set(user_groups.values_list("name", flat=True))
            required_group_names = set(groups)

            if not (user_group_names & required_group_names):
                raise PermissionDenied(
                    "User %s not in required groups: %s"
                    % (request.user, required_group_names)
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
