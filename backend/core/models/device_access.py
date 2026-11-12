"""Durable user-visible authorization, independent of rotating token values."""

import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class DeviceAccess(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token_family = models.UUIDField(unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    application = models.ForeignKey(
        settings.OAUTH2_PROVIDER_APPLICATION_MODEL, on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100, default="Python access")
    authorized_at = models.DateTimeField(default=timezone.now)
    last_renewed_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-authorized_at"]
