import logging

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
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


def saml2_template_failure(request, exception=None, status=403, **kwargs):
    """Renders a simple template with an error message."""

    logger = logging.getLogger("saml")
    logger.debug("------------------------------------------")
    logger.debug("saml2_template_failure()")
    logger.debug(f"request: {request}")
    logger.debug(f"exception: {exception}")
    logger.debug(f"status: {status}")
    logger.debug(f"kwargs: {kwargs}")

    needs_registration = request.session.get("needs_registration", False)
    pending_approval = request.session.get("pending_approval", False)
    user_status = request.session.get("user_status")

    logger.debug(f"needs_registration: {needs_registration}")
    logger.debug(f"pending_approval: {pending_approval}")
    logger.debug(f"user_status: {user_status}")

    if needs_registration:
        logger.info("Redirecting to Rubin registration page.")
        return render(
            request,
            "djangosaml2/rubin_need_registration.html",
            {"exception": exception},
            status=status,
        )

    if pending_approval:
        logger.info(
            f"User status is {user_status}. Redirecting to waiting aproval error page."
        )
        return render(
            request,
            "djangosaml2/waiting_approval.html",
            {"exception": exception},
            status=status,
        )

    return render(
        request, "djangosaml2/login_error.html", {"exception": exception}, status=status
    )


@api_view(["GET"])
@permission_classes([AllowAny])
def teste(request):
    if request.method == "GET":
        return render(request, "djangosaml2/login_error.html")
    return None


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
