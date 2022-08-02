from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view


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