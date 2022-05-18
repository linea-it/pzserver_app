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
from django.urls import path, re_path, include
from rest_framework import routers

# from core.api import viewsets as products_viewsets
from core.views import (
    ReleaseViewSet,
    ProductViewSet,
    ProductTypeViewSet,
    TestGithubAuth,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

route = routers.DefaultRouter()

route.register(r"releases", ReleaseViewSet, basename="Releases")
route.register(r"product-types", ProductTypeViewSet, basename="ProductTypes")
route.register(r"products", ProductViewSet, basename="Products")


urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(r"^auth/", include("drf_social_oauth2.urls", namespace="social")),
    re_path(r"^auth/", include("drf_social_oauth2.urls", namespace="drf")),
    path("api/", include(route.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/github/", TestGithubAuth.as_view()),
]
