"""Authentication through explicitly trusted partner JupyterHubs."""

from urllib.parse import urlsplit

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed


class HubUnavailable(APIException):
    status_code = 503
    default_detail = "Partner JupyterHub is unavailable. Try again later."
    default_code = "hub_unavailable"


class JupyterHubAuthentication(BaseAuthentication):
    """Accept ``Authorization: JupyterHub <partner-id> <hub-token>``.

    Only server-configured HTTPS endpoints are contacted. The verified Hub
    username must exactly match an active local account. Hub groups and admin
    flags never grant local rights.
    """

    def authenticate_header(self, request):
        return "JupyterHub"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != b"jupyterhub":
            return None
        if len(parts) != 3:
            raise AuthenticationFailed("Malformed JupyterHub authorization.")
        try:
            partner_id, token = (part.decode("ascii") for part in parts[1:])
        except UnicodeDecodeError:
            raise AuthenticationFailed("Malformed JupyterHub authorization.") from None

        partner = getattr(settings, "JUPYTERHUB_PARTNERS", {}).get(partner_id)
        if not partner or partner.get("enabled") is not True:
            raise AuthenticationFailed("Unknown or disabled JupyterHub partner.")
        endpoint = partner.get("user_url", "")
        parsed = urlsplit(endpoint)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.query
            or parsed.fragment
        ):
            raise HubUnavailable()

        try:
            response = requests.get(
                endpoint,
                headers={"Authorization": f"token {token}"},
                timeout=(5, 10),
                allow_redirects=False,
            )
        except requests.RequestException:
            raise HubUnavailable() from None
        try:
            if response.status_code in (401, 403):
                raise AuthenticationFailed("Invalid JupyterHub credential.")
            if response.status_code != 200:
                raise HubUnavailable()
            try:
                identity = response.json()
            except ValueError:
                raise HubUnavailable() from None
        finally:
            response.close()

        if not isinstance(identity, dict) or identity.get("kind") != "user":
            raise AuthenticationFailed("A JupyterHub user identity is required.")
        name = identity.get("name")
        if not isinstance(name, str) or not name:
            raise AuthenticationFailed("Invalid JupyterHub identity.")
        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=name, is_active=True)
        except (user_model.DoesNotExist, user_model.MultipleObjectsReturned):
            raise AuthenticationFailed("No matching active PzServer account.") from None
        # Enforce exact matching even if the database uses a case-insensitive collation.
        if user.username != name:
            raise AuthenticationFailed("No matching active PzServer account.")
        # Do not retain the bearer secret in request.auth or return it to clients.
        return user, {"partner": partner_id, "hub_user": name}
