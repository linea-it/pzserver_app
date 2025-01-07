"""pzserver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from core.api import viewsets as products_viewsets
from core.views import (CsrfToOauth, GetToken, LoggedUserView, Logout,
                        OrchestrationInfoView, OrchestrationPipelinesView,
                        PipelineViewSet, ProcessViewSet, ProductContentViewSet,
                        ProductFileViewSet, ProductTypeViewSet, ProductViewSet,
                        ProductSpeczViewSet, ReleaseViewSet, UserViewSet, which_environment)
from django.conf import settings

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework import routers

route = routers.DefaultRouter()

route.register(r"users", UserViewSet, basename="users")
route.register(r"releases", ReleaseViewSet, basename="releases")
route.register(r"product-types", ProductTypeViewSet, basename="product_types")
route.register(r"products", ProductViewSet, basename="products")
route.register(r"products-specz", ProductSpeczViewSet, basename="products_specz")
route.register(r"product-contents", ProductContentViewSet, basename="product_contents")
route.register(r"product-files", ProductFileViewSet, basename="product_files")

if settings.ORCHEST_URL:
    route.register(r"pipelines", PipelineViewSet, basename="pipelines")
    route.register(r"processes", ProcessViewSet, basename="processes")

from rest_framework.authtoken import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(route.urls)),
    path("api/which_environment/", which_environment),
    # Autenticacao
    path("api/auth/", include("drf_social_oauth2.urls", namespace="drf")),
    path("api/obtain_token/", views.obtain_auth_token),
    path("api/get_token/", GetToken.as_view(), name="get_token"),
    path("api/csrf_oauth/", CsrfToOauth.as_view()),
    path("api/logged_user/", LoggedUserView.as_view(), name="logged_user"),
    path("api/logout/", Logout.as_view(), name="logout"),
    # API DOCs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path(r"saml2/", include('djangosaml2.urls')),
]

if settings.ORCHEST_URL:
    urlpatterns.append(path("api/sysinfo/", OrchestrationInfoView.as_view()))
    urlpatterns.append(path("api/orch_pipelines/", OrchestrationPipelinesView.as_view()))
