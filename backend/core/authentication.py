"""Authentication through explicitly trusted partner JupyterHubs."""

import json

import requests
from core.hub_urls import normalize_hub_url
from core.models import JupyterHubConsent, TrustedJupyterHub
from django.contrib.auth import get_user_model
from django.core.cache import caches
from django.utils.crypto import salted_hmac
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed


class HubUnavailable(APIException):
    status_code = 503
    default_detail = "Partner JupyterHub is unavailable. Try again later."
    default_code = "hub_unavailable"


class JupyterHubAuthentication(BaseAuthentication):
    """Accept ``Authorization: JupyterHub <hub-url> <hub-token>``.

    Only server-configured HTTPS endpoints are contacted. The verified Hub
    username must exactly match an active local account. Hub groups and admin
    flags never grant local rights.
    """

    def authenticate_header(self, request):
        parts = get_authorization_header(request).split()
        if parts and parts[0].lower() == b"jupyterhub":
            return "JupyterHub"
        return OAuth2Authentication().authenticate_header(request)

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts or parts[0].lower() != b"jupyterhub":
            return None
        if len(parts) != 3:
            raise AuthenticationFailed("Malformed JupyterHub authorization.")
        try:
            hub_url, token = (part.decode("ascii") for part in parts[1:])
        except UnicodeDecodeError:
            raise AuthenticationFailed("Malformed JupyterHub authorization.") from None

        try:
            hub_url = normalize_hub_url(hub_url)
        except ValueError:
            raise AuthenticationFailed("Invalid JupyterHub URL.") from None
        # Include disabled entries when detecting ambiguity; never try another Hub.
        matches = [
            hub
            for hub in TrustedJupyterHub.objects.all()
            if hub_url in [hub.public_url, *hub.aliases]
        ]
        if len(matches) > 1:
            raise HubUnavailable()
        if not matches or not matches[0].enabled:
            raise AuthenticationFailed("Unknown or disabled JupyterHub partner.")
        partner = matches[0]
        partner_id = partner.public_url
        endpoint = partner.user_url
        try:
            normalize_hub_url(endpoint)
        except ValueError:
            raise HubUnavailable() from None

        cache = caches["jupyterhub"]
        cache_key = (
            "hub-auth:v1:"
            + salted_hmac(
                "jupyterhub-validation",
                json.dumps([partner.pk, partner.consent_signature, token]),
                algorithm="sha256",
            ).hexdigest()
        )
        name = cache.get(cache_key)
        cache_miss = name is None
        if cache_miss:
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
        # Recheck partner state after the upstream request (configuration may change).
        current = TrustedJupyterHub.objects.filter(pk=partner.pk, enabled=True).first()
        if current is None or current.consent_signature != partner.consent_signature:
            raise AuthenticationFailed("JupyterHub configuration changed. Try again.")
        if not JupyterHubConsent.objects.filter(
            user=user,
            hub=partner,
            enabled=True,
            hub_signature=partner.consent_signature,
        ).exists():
            raise AuthenticationFailed(
                "Authorize this Hub in PzServer at /hub_access before using notebook access.",
                code="hub_consent_required",
            )
        if cache_miss:
            # Cache successful authentications only; hits never extend the TTL.
            cache.set(cache_key, name, timeout=300)
        # Do not retain the bearer secret in request.auth or return it to clients.
        return user, {"partner": partner_id, "hub_user": name}
