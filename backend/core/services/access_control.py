import logging
from typing import Optional

from core.models import Product, Release
from django.contrib.auth.models import Group, User
from django.db.models import Q, QuerySet

log = logging.getLogger("saml")


class AccessControlService:
    """
    Service for managing access control based on Linea IdP groups.
    """

    @staticmethod
    def get_user_groups(user: User) -> QuerySet[Group]:
        """
        Returns the Django groups to which the user belongs.

        Args:
            user: User model instance

        Returns:
            QuerySet with user groups
        """
        return user.groups.all()

    @staticmethod
    def user_can_access_release(user: User, release: Release) -> bool:
        """
        Checks if the user can access a specific release.

        Args:
            user: User model instance
            release: Release model instance

        Returns:
            bool: True if the user can access the release
        """
        return release.user_has_access(user)

    @staticmethod
    def user_can_access_product(user: User, product: Product) -> bool:
        """
        Checks if the user can access a specific product.

        Args:
            user: User model instance
            product: Product model instance

        Returns:
            bool: True if the user can access the product
        """
        return product.user_has_access(user)

    @staticmethod
    def filter_accessible_releases(
        user: User, queryset: Optional[QuerySet] = None
    ) -> QuerySet[Release]:
        """
        Filters releases to which the user has access.

        Args:
            user: User model instance
            queryset: Optional QuerySet of releases to filter

        Returns:
            QuerySet with releases accessible to the user
        """
        if queryset is None:
            queryset = Release.objects.all()

        # Administrators have access to everything
        log.info("user is admin?")
        log.info(user.profile.is_admin())
        if user.profile.is_admin():
            return queryset

        # Get user group IDs
        user_group_ids = list(
            AccessControlService.get_user_groups(user).values_list("id", flat=True)
        )

        log.info(f"user groups: {user_group_ids}")

        # Use Q objects to combine conditions
        return queryset.filter(
            Q(is_public=True)  # Public releases
            | Q(access_groups__isnull=True)  # Releases without defined groups
            | Q(access_groups__id__in=user_group_ids)  # Releases with user groups
        ).distinct()

    @staticmethod
    def filter_accessible_products(
        user: User, queryset: Optional[QuerySet] = None
    ) -> QuerySet[Product]:
        """
        Filters products to which the user has access based on the release.

        Args:
            user: User model instance
            queryset: Optional QuerySet of products to filter

        Returns:
            QuerySet with products accessible to the user
        """
        if queryset is None:
            queryset = Product.objects.all()

        # Administrators have access to everything
        if user.profile.is_admin():
            return queryset

        # Get accessible releases
        accessible_releases = AccessControlService.filter_accessible_releases(user)

        return queryset.filter(
            Q(user=user)  # Products created by the user themselves
            | Q(release__isnull=True)  # Products without release
            | Q(release__in=accessible_releases)  # Products with accessible releases
        ).distinct()

    @staticmethod
    def get_group_members(group: Group) -> QuerySet[User]:
        """
        Returns the users who are members of a specific group.

        Args:
            group: Group model instance

        Returns:
            QuerySet with users who are members of the group
        """
        return group.user_set.all()

    @staticmethod
    def add_user_to_group(user: User, group: Group) -> bool:
        """
        Adds a user to a Django group.

        Args:
            user: User model instance
            group: Group model instance

        Returns:
            bool: True if the addition was successful
        """
        try:
            if not user.groups.filter(id=group.id).exists():
                user.groups.add(group)
                return True
            return True  # Already in the group
        except Exception:
            return False

    @staticmethod
    def remove_user_from_group(user: User, group: Group, force: bool = False) -> bool:
        """
        Removes a user from a Django group.
        WARNING: For Linea groups, this may be reverted in the next synchronization.

        Args:
            user: User model instance
            group: Group model instance
            force: If True, removes even if it's a Linea group

        Returns:
            bool: True if the removal was successful
        """
        try:
            # Check if it's a Linea group
            if (
                hasattr(group, "metadata")
                and group.metadata.is_linea_group
                and not force
            ):
                raise ValueError(
                    f"Cannot remove user from Linea group '{group.name}' "
                    "without force=True. The removal will be reverted in the next synchronization."
                )

            user.groups.remove(group)
            return True
        except Exception:
            return False
