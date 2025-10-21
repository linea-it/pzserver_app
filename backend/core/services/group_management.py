import logging
from typing import List

from core.models import GroupMetadata
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.utils import timezone

log = logging.getLogger("group_management")


class GroupManagementService:
    """
    Unified service for managing user-group relationships.
    """

    @staticmethod
    def add_user_to_group(user: User, group: Group) -> bool:
        """
        Adds a user to a group.

        Args:
            user: User instance
            group: Group instance

        Returns:
            Boolean indicating success
        """
        try:
            with transaction.atomic():
                if not user.groups.filter(id=group.id).exists():
                    user.groups.add(group)

                log.debug(f"User {user.username} added to group {group.name} ")

                return True

        except Exception as e:
            log.error(f"Error adding user {user.username} to group {group.name}: {e}")
            raise

    @staticmethod
    def remove_user_from_group(user: User, group: Group) -> bool:
        """
        Removes a user from a group.

        Args:
            user: User instance
            group: Group instance

        Returns:
            True if removal was successful
        """
        try:
            with transaction.atomic():
                if user.groups.filter(id=group.id).exists():
                    user.groups.remove(group)

                log.debug(f"User {user.username} removed from group {group.name}")
                return True

        except Exception as e:
            log.error(
                f"Error removing user {user.username} from group {group.name}: {e}"
            )
            raise

    @staticmethod
    def get_user_groups(user: User) -> List[Group]:
        """
        Gets all groups for a user.

        Args:
            user: User instance

        Returns:
            List of Group instances
        """
        return list(user.groups.all())

    @staticmethod
    def get_group_members(group: Group) -> List[User]:
        """
        Gets all members of a group.

        Args:
            group: Group instance

        Returns:
            List of User instances
        """
        return list(group.user_set.all())

    @staticmethod
    def sync_linea_groups(user: User, linea_group_names: List[str]) -> None:
        """
        Synchronizes user's Linea groups.
        This method replaces the logic in SAML2 backend to avoid duplication.

        Args:
            user: User instance
            linea_group_names: List of group names from Linea IdP
        """
        try:
            with transaction.atomic():
                current_linea_groups = []

                # Add/update current groups
                for group_name in linea_group_names:
                    if not isinstance(group_name, str):
                        continue

                    group_name = group_name.strip()
                    if not group_name:
                        continue

                    # Create or get Django group
                    django_group, group_created = Group.objects.get_or_create(
                        name=group_name
                    )
                    current_linea_groups.append(django_group)

                    # Create or update group metadata
                    metadata, metadata_created = GroupMetadata.objects.get_or_create(
                        group=django_group,
                        defaults={
                            "source": GroupMetadata.GroupSource.LINEA,
                            "display_name": group_name.title(),
                            "description": f"LIneA group created automatically: {group_name}",
                            "last_sync": timezone.now(),
                        },
                    )

                    # If it already existed but wasn't LIneA, convert to LIneA
                    if not metadata_created and not metadata.is_linea_group:
                        log.warning(
                            f"Group {group_name} existed as LOCAL, converting to LIneA"
                        )
                        metadata.source = GroupMetadata.GroupSource.LINEA
                        metadata.save(update_fields=["source"])

                    # Update sync timestamp for LIneA groups
                    if metadata.is_linea_group:
                        metadata.last_sync = timezone.now()
                        metadata.save(update_fields=["last_sync"])

                    # Add user to group using unified method
                    GroupManagementService.add_user_to_group(
                        user=user, group=django_group
                    )

                # Remove groups no longer present
                GroupManagementService._remove_missing_linea_groups(
                    user, current_linea_groups
                )

        except Exception as e:
            log.error(f"Error synchronizing Linea groups for user {user.username}: {e}")
            raise

    @staticmethod
    def _remove_missing_linea_groups(
        user: User, current_linea_groups: List[Group]
    ) -> None:
        """
        Removes user from Linea groups that are no longer present.

        Args:
            user: User instance
            current_linea_groups: List of current Linea groups
        """
        current_group_ids = [g.id for g in current_linea_groups]

        # Find Linea-managed groups that the user had but are no longer present
        linea_user_groups = user.groups.filter(
            metadata__source=GroupMetadata.GroupSource.LINEA
        )

        for group in linea_user_groups:
            try:
                if group.id not in current_group_ids:
                    user.groups.remove(group)
                log.debug(
                    f"User {user.username} removed from Linea group {group.name} "
                    f"(no longer present in IdP)"
                )
            except Exception as e:
                log.error(
                    f"Error removing user {user.username} from group {group.name}: {e}"
                )
        user.save()
