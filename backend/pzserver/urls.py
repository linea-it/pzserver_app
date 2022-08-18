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
    ProductContentViewSet,
    ProductFileViewSet,
    TestGithubAuth,
    LoggedUserView,
    get_token,
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

from rest_framework.authtoken import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # path("auth/", include("drf_social_oauth2.urls", namespace="social")),
    path("auth/", include("drf_social_oauth2.urls", namespace="drf")),
    path("api/", include(route.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("api/obtain_token/", views.obtain_auth_token),
    path("api/get_token", get_token),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/github/", TestGithubAuth.as_view()),
    path("api/logged_user/", LoggedUserView.as_view()),
    # path("api/shib/$", ShibbolethView.as_view(), name="info"),
    # path("api/shib/login/$", ShibbolethLoginView.as_view(), name="login"),
    # path("api/shib/logout/$", ShibbolethLogoutView.as_view(), name="logout"),
    path("api/shib/", include("core.shibboleth_urls", namespace="shibboleth")),
    # path('api/accounts/', include('django.contrib.auth.urls')),
]
