"""Opt-in guarded OAuth device endpoints; no client registration endpoints."""

from django.urls import path
from oauth2_provider import views
from core.views.device_oauth import (
    DeviceAuthorizationView,
    DeviceCancelView,
    DeviceTokenView,
    DeviceUserCodeView,
    DeviceConfirmView,
    DeviceGrantStatusView,
)

app_name = "oauth2_provider"
urlpatterns = [
    path("cancel/", DeviceCancelView.as_view(), name="device-cancel"),
    path(
        "device-authorization/",
        DeviceAuthorizationView.as_view(),
        name="device-authorization",
    ),
    path("device/", DeviceUserCodeView.as_view(), name="device"),
    path(
        "device-confirm/<slug:client_id>/<slug:user_code>",
        DeviceConfirmView.as_view(),
        name="device-confirm",
    ),
    path(
        "device-grant-status/<slug:client_id>/<slug:user_code>",
        DeviceGrantStatusView.as_view(),
        name="device-grant-status",
    ),
    path("token/", DeviceTokenView.as_view(), name="token"),
    path("revoke_token/", views.RevokeTokenView.as_view(), name="revoke-token"),
]
