import logging
from typing import Dict

from core.services.group_management import GroupManagementService
from django.contrib.auth.models import User
from djangosaml2.backends import Saml2Backend

log = logging.getLogger("saml")


class CustomSaml2Backend(Saml2Backend):
    """
    Custom SAML backend for LIneA that:
        - Validates user status (active, pending, etc.)
        - Synchronizes groups based on the 'member' key
        - Redirects inactive users to registration
    """

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
        Now uses GroupManagementService to eliminate duplication.

        Args:
            user: User model instance
            attributes: Dictionary with SAML attributes
        """
        member_groups = attributes.get("isMemberOf", [])
        if not member_groups:
            log.debug(f"No groups found in 'isMemberOf' key for user {user.username}")
            return

        log.debug(f"LIneA groups found for {user.username}: {member_groups}")

        try:
            # Use the unified service to sync groups without duplication
            GroupManagementService.sync_linea_groups(user, member_groups)
        except Exception as e:
            log.error(
                f"Error synchronizing LIneA groups for user {user.username}: {str(e)}"
            )
