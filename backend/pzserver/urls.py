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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

# from core.api import viewsets as products_viewsets
from core.views import (
    ReleaseViewSet,
    ProductViewSet,
    ProductTypeViewSet,
    ProductContentViewSet,
    ProductFileViewSet,
    LoggedUserView,
    get_token,
    CsrfToOauth,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

route = routers.DefaultRouter()

route.register(r"releases", ReleaseViewSet, basename="Releases")

route.register(r"product-files", ProductFileViewSet, basename="ProductFiles")
route.register(r"product-contents", ProductContentViewSet, basename="ProductContents")
route.register(r"product-types", ProductTypeViewSet, basename="ProductTypes")
route.register(r"products", ProductViewSet, basename="Products")


from shibboleth.views import ShibbolethView, ShibbolethLogoutView, ShibbolethLoginView
from rest_framework.authtoken import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(route.urls)),
    # Autenticacao
    path("api/auth/", include("drf_social_oauth2.urls", namespace="drf")),
    path("api/obtain_token/", views.obtain_auth_token),
    path("api/get_token", get_token),
    path("api/csrf_oauth/", CsrfToOauth.as_view()),
    path("api/logged_user/", LoggedUserView.as_view()),
    path("api/shib/", include("core.shibboleth_urls", namespace="shibboleth")),
    # API DOCs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
