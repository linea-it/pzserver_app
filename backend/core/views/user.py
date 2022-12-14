import logging

import requests
from core.serializers.user import UserSerializer
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.models import Group, User
from django.http import HttpResponseRedirect
from django.utils import timezone
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauthlib.common import generate_token
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LoggedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # `django.contrib.auth.User` instance.
        username = str(request.user)
        if (
            request.user.profile is not None
            and request.user.profile.display_name is not None
            and request.user.profile.display_name != ""
        ):
            username = request.user.profile.display_name

        is_admin = request.user.profile.is_admin()

        content = {"username": username, "is_admin": is_admin}
        return Response(content)


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def logout(request):
class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        if settings.SHIBBOLETH_ENABLED:
            try:
                log = logging.getLogger("shibboleth")
                log.debug(f"User {request.user} request logout ")
                shib_logout_uri = request.build_absolute_uri("/Shibboleth.sso/Logout")
                log.debug(f"Logout URL: {shib_logout_uri}")
                r = requests.get(shib_logout_uri)
                if r.status_code == 200:
                    log.debug(f"Logout Success")
                else:
                    log.error(f"User {request.user} Logout Failed. {str(r)}")
            except Exception as e:
                log.error(f"User {request.user} Logout Failed. {str(e)}")

        logout(request)

        return Response(status=status.HTTP_200_OK)


class GetToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        """_Cria um novo token para o usuario logado.
            Sempre que este metodo for executado um novo token sera criado,
            Caso o usuario já possua um token ele será removido e um novo será criado.
        Returns:
            dict: {token: str}
        """
        try:
            token = Token.objects.get(user=request.user)
            token.delete()
            token = Token.objects.create(user=request.user)
        except:
            token = Token.objects.create(user=request.user)
        return Response(dict({"token": token.key}))


class CsrfToOauth(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        log = logging.getLogger("django")
        log.debug("----------------------------------")
        log.debug("Change Csrf Token to Oauth Token")

        client_id = request.data.get("client_id", None)
        if client_id is None:
            return Response(
                {"error": "client_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        log.debug(f"Client ID: {client_id}")

        try:
            app = Application.objects.get(client_id=client_id)
        except Application.DoesNotExist:
            return Response(
                {
                    "error": "The application linked to the provided client_id could not be found."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        log.debug(f"Application: {app}")

        user = request.user
        log.debug(f"User: {user}")

        expire_seconds = settings.OAUTH2_PROVIDER.get(
            "ACCESS_TOKEN_EXPIRE_SECONDS", 36000
        )
        log.debug(f"Expire Seconds: {expire_seconds}")

        access_token = AccessToken.objects.create(
            user=user,
            token=generate_token(),
            application=app,
            expires=timezone.now() + relativedelta(seconds=expire_seconds),
            scope="read write",
        )
        log.debug(f"Access Token : {access_token}")

        refresh_token = RefreshToken(
            user=user,
            token=generate_token(),
            application=app,
            access_token=access_token,
        )
        log.debug(f"Refresh Token: {refresh_token}")

        # Usando O Backend para criar os tokens no cookie
        response = HttpResponseRedirect(redirect_to="/")

        response.set_cookie(
            "pzserver.access_token",
            str(access_token),
            expires=expire_seconds,
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE or None,
        )
        response.set_cookie(
            "pzserver.refresh_token",
            str(refresh_token),
            max_age=(30 * 24 * 60 * 60),
            domain=settings.SESSION_COOKIE_DOMAIN,
            secure=settings.SESSION_COOKIE_SECURE or None,
        )
        return response


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    ordering = ["username"]
