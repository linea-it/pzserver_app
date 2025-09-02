from core.maestro import Maestro
from core.views.pipeline import PipelineViewSet
from core.views.process import ProcessViewSet
from core.views.product import ProductSpeczViewSet, ProductViewSet
from core.views.product_content import ProductContentViewSet
from core.views.product_file import ProductFileViewSet
from core.views.product_type import ProductTypeViewSet
from core.views.release import ReleaseViewSet
from core.views.user import CsrfToOauth, GetToken, LoggedUserView, Logout, UserViewSet
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


@api_view(["GET"])
@permission_classes([AllowAny])
def which_environment(request):

    if request.method == "GET":
        env_name = settings.ENVIRONMENT_NAME

        dev_env = ["Development", "development", "dev", "Staging", "Homolog"]
        is_dev = True if env_name in dev_env else False
        result = {"enviroment_name": settings.ENVIRONMENT_NAME, "is_dev": is_dev}
        return Response(result)


class OrchestrationInfoView(APIView):

    http_method_names = [
        "get",
    ]

    def get(self, request):
        try:
            maestro = Maestro(url=settings.ORCHEST_URL)
            data = maestro.sysinfo()
            processing_dir = data.get("processing_dir", "")
            if processing_dir != settings.PROCESSING_DIR:
                raise ValueError(
                    (
                        f"PROCESSING_DIR ({settings.PROCESSING_DIR}) is "
                        f"different in the orchestration: {processing_dir}"
                    )
                )
            code_status = status.HTTP_200_OK
        except Exception as err:
            data = {"error": str(err)}
            code_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data, status=code_status)


class OrchestrationPipelinesView(APIView):

    http_method_names = [
        "get",
    ]

    def get(self, request):
        try:
            maestro = Maestro(url=settings.ORCHEST_URL)
            data = maestro.pipelines()
            code_status = status.HTTP_200_OK
        except Exception as err:
            data = {"error": str(err)}
            code_status = status.HTTP_500_INTERNAL_SERVER_ERROR

        return Response(data, status=code_status)
