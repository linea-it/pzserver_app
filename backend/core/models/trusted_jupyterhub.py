import hashlib
import json

from core.hub_urls import normalize_hub_url
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone


class TrustedJupyterHub(models.Model):
    name = models.CharField(max_length=255)
    public_url = models.URLField(max_length=2048, unique=True)
    aliases = models.JSONField(
        default=list, blank=True, help_text="JSON list of alternate public HTTPS URLs."
    )
    user_url = models.URLField(
        max_length=2048, help_text="Fixed HTTPS endpoint returning the token owner."
    )
    enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "trusted JupyterHub"
        verbose_name_plural = "trusted JupyterHubs"

    def __str__(self):
        return self.name

    @property
    def consent_signature(self):
        identity = [self.public_url, self.user_url, sorted(self.aliases)]
        return hashlib.sha256(json.dumps(identity).encode()).hexdigest()

    def clean(self):
        super().clean()
        if not isinstance(self.aliases, list):
            raise ValidationError({"aliases": "Use a JSON list of HTTPS URLs."})
        try:
            self.public_url = normalize_hub_url(self.public_url)
            self.aliases = [normalize_hub_url(url) for url in self.aliases]
            # Validate without changing the endpoint path (its trailing slash may matter).
            normalize_hub_url(self.user_url)
        except ValueError as exc:
            raise ValidationError(str(exc)) from exc
        addresses = [self.public_url, *self.aliases]
        if len(set(addresses)) != len(addresses):
            raise ValidationError(
                {"aliases": "Duplicate URL or alias after normalization."}
            )
        for other in type(self).objects.exclude(pk=self.pk):
            if set(addresses).intersection([other.public_url, *other.aliases]):
                raise ValidationError(
                    {"aliases": "A URL is already registered to another Hub."}
                )

    def save(self, *args, **kwargs):
        with transaction.atomic():
            previous = (
                type(self).objects.select_for_update().filter(pk=self.pk).first()
                if self.pk
                else None
            )
            self.full_clean()
            result = super().save(*args, **kwargs)
            if previous and previous.consent_signature != self.consent_signature:
                self.jupyterhubconsent_set.filter(enabled=True).update(
                    enabled=False, revoked_at=timezone.now()
                )
            return result
