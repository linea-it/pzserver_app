from rest_framework import views
from django.http import JsonResponse
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope


class TestGithubAuth(views.APIView):
    permission_classes = (TokenHasReadWriteScope,)

    def get(self, request):
        return JsonResponse({"user": str(request.user)})
