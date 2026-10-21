from django.conf import settings
from django.db import models


class JupyterHubConsent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hub = models.ForeignKey("core.TrustedJupyterHub", on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    hub_signature = models.CharField(max_length=64)
    authorized_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "hub"], name="unique_user_hub_consent"
            )
        ]
