import uuid
from django.db import models
from django.utils import timezone


class DeviceAuthorizationAttempt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    grant = models.OneToOneField(
        "oauth2_provider.DeviceGrant", on_delete=models.CASCADE, swappable=False
    )
    errors = models.PositiveSmallIntegerField(default=0)


class DeviceRateLimit(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    started_at = models.DateTimeField(default=timezone.now, db_index=True)
    count = models.PositiveIntegerField(default=0)
