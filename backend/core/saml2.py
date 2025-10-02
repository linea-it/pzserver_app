import logging
from typing import Any, Dict, List

from core.models import GroupMembership, GroupMetadata
from django.contrib import messages
from django.contrib.auth.models import Group, User
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from djangosaml2.backends import Saml2Backend

log = logging.getLogger("saml")


class LineaSaml2Backend(Saml2Backend):
    """
    Custom SAML backend for LIneA that:
        - Validates user status (active, pending, etc.)
        - Synchronizes groups based on the 'member' key
        - Redirects inactive users to registration
    """

    # Statuses that indicate pending registration
    PENDING_STATUSES = [
        "Pending",
        "PendingApproval",
        "PendingConfirmation",
        "PendingVetting",
    ]

    ACTIVE_STATUS = "Active"

    def authenticate(
        self, request, session_info=None, attribute_mapping=None, **kwargs
    ):
        """
        Override the authentication method to validate user status.
        """
        if session_info is None:
            log.debug("No SAML session information provided")
            return None

        attributes = session_info.get("ava", {})
        log.debug(f"SAML attributes: {attributes}")

        # Validate user status before proceeding
        user_status = self._get_user_status(attributes)
        request.session["user_status"] = user_status
        log.info(f"Extracted user status: {user_status}")

        auth_info = attributes.get("knowledgeInformation", "Not informed")
        log.info(f"User knowledgeInformation: {auth_info}")

        # get uid
        uid = attributes.get("uid", None)
        if uid and isinstance(uid, list):
            uid = uid[0]

        if not uid:
            log.warning("No UID found in SAML attributes")
            request.session["needs_registration"] = True
            return None

        if user_status in self.PENDING_STATUSES:
            log.info(
                (
                    "Your registration is pending approval. "
                    "Please wait for confirmation or contact support."
                )
            )
            request.session["pending_approval"] = True
            return None

        elif user_status != self.ACTIVE_STATUS:
            log.error(f"User with inactive status: {user_status}")
            return None

        # If user is active, proceed with normal authentication
        return super().authenticate(request, session_info, attribute_mapping, **kwargs)

    def _get_user_status(self, attributes: Dict) -> str:
        """
        Extracts user status from SAML attributes.

        Args:
            attributes: Dictionary with SAML attributes

        Returns:
            User status or 'Unknown' if not found
        """
        status_list = attributes.get("schacUserStatus", [])
        if isinstance(status_list, list) and len(status_list) > 0:
            return status_list[0]
        elif isinstance(status_list, str):
            return status_list

        log.warning("User status not found in SAML attributes")
        return "Unknown"

    def _update_user(
        self,
        user: User,
        attributes: Dict,
        attribute_mapping: Dict,
        force_save: bool = False,
    ):
        """
        Updates user information and synchronizes groups.

        Args:
            user: User model instance
            attributes: Dictionary with received SAML attributes
            attribute_mapping: Attribute mapping
            force_save: Whether to force save
        """
        log.debug(f"Updating user: {user.username}")
        log.debug(f"Received attributes: {attributes}")

        # Update basic user information
        self._update_user_info(user, attributes)

        # Synchronize LIneA groups
        self._sync_linea_groups(user, attributes)

        return super()._update_user(user, attributes, attribute_mapping, force_save)

    def _update_user_info(self, user: User, attributes: Dict) -> None:
        """
        Updates basic user information based on SAML attributes.

        Args:
            user: User model instance
            attributes: Dictionary with SAML attributes
        """
        # Update full name
        display_name = attributes.get("displayName", [])
        if display_name and len(display_name) > 0:
            full_name = display_name[0]
            name_parts = full_name.split()
            if len(name_parts) >= 2:
                user.first_name = name_parts[0]
                user.last_name = " ".join(name_parts[1:])
            elif len(name_parts) == 1:
                user.first_name = name_parts[0]

        # Update email
        email = attributes.get("email", [])
        if email and len(email) > 0:
            user.email = email[0]

        user.save()

        # Update profile if it exists
        if hasattr(user, "profile"):
            if display_name and len(display_name) > 0:
                user.profile.display_name = display_name[0]
                user.profile.save()

    def _sync_linea_groups(self, user: User, attributes: Dict) -> None:
        """
        Synchronizes user groups based on LIneA groups from 'member' key.

        Args:
            user: User model instance
            attributes: Dictionary with SAML attributes
        """
        member_groups = attributes.get("member", [])
        if not member_groups:
            log.debug(f"No groups found in 'member' key for user {user.username}")
            return

        log.debug(f"LIneA groups found for {user.username}: {member_groups}")

        try:
            with transaction.atomic():
                current_linea_groups = []

                for group_name in member_groups:
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

                    if group_created:
                        log.info(f"Created new Django group: {group_name}")
                    if metadata_created:
                        log.info(f"Created LIneA metadata for group: {group_name}")

                    # Add user to Django group (if not already in it)
                    if not user.groups.filter(id=django_group.id).exists():
                        user.groups.add(django_group)
                        log.debug(
                            f"User {user.username} added to Django group {group_name}"
                        )

                    # Create LIneA tracking (if not already exists)
                    linea_membership, membership_created = (
                        GroupMembership.objects.get_or_create(
                            user=user, group=django_group
                        )
                    )
                    
                    if not membership_created:
                        log.debug(
                            f"LIneA association already exists for user {user.username} with group {group_name}"
                        )

                # Delete LIneA group memberships that are no longer present
                self._remove_missing_linea_groups(user, current_linea_groups)

        except Exception as e:
            log.error(
                f"Error synchronizing LIneA groups for user {user.username}: {str(e)}"
            )

    def _remove_missing_linea_groups(
        self, user: User, current_linea_groups: List[Group]
    ) -> None:
        """
        Removes user from LIneA groups that are no longer present and deletes tracking records.

        Args:
            user: User
            current_linea_groups: List of current LIneA groups
        """
        current_group_ids = [g.id for g in current_linea_groups]

        # Find LIneA groups that the user had but are no longer present
        outdated_memberships = GroupMembership.objects.filter(
            user=user
        ).exclude(group__id__in=current_group_ids)

        for membership in outdated_memberships:
            group = membership.group

            # Remove user from Django group only if it's a LIneA group
            if hasattr(group, "metadata") and group.metadata.is_linea_group:
                user.groups.remove(group)
                log.debug(
                    f"User {user.username} removed from LIneA group {group.name} "
                    f"(no longer present in IdP)"
                )
            else:
                log.warning(
                    f"Group {group.name} was being tracked but doesn't have correct LIneA metadata"
                )
            
            # Delete the membership tracking record
            membership.delete()
            log.debug(
                f"Deleted GroupMembership record for user {user.username} and group {group.name}"
            )
