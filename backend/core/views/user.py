from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class LoggedUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        content = {
            "username": str(request.user),  # `django.contrib.auth.User` instance.
        }
        return Response(content)
