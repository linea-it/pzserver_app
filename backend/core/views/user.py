from email.mime import application
from http import client
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
import logging


class LoggedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            "username": str(request.user),  # `django.contrib.auth.User` instance.
        }
        return Response(content)


@api_view(["POST"])
def get_token(request):
    if request.method == "POST":
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

    def get(self, request, format=None):
        log = logging.getLogger("django")
        log.debug("----------------------------------")
        log.debug("Change Csrf Token to Oauth Token")

        from oauthlib.common import generate_token
        from oauth2_provider.models import AccessToken, RefreshToken, Application
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        from django.conf import settings
        from rest_framework import status
        from django.http import HttpResponseRedirect

        app = Application.objects.get(
            client_id="lKPub4YnYGeUq77VIys0gGPoDh25NB0oKv4vwH5G"
        )
        log.debug(f"App: {app}")
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

        # # Usando o Frontend para criar os cookie e fazer o signin
        # content = {
        #     "access_token": str(access_token),
        #     "refresh_token": str(refresh_token),
        #     "expires_in": expire_seconds,
        # }
        # response = Response(content, status=status.HTTP_200_OK)

        # return response

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
