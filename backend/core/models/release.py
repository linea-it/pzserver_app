from django.db import models


class Release(models.Model):
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    indexing_column = models.CharField(max_length=255)
    has_mag_hats = models.BooleanField(default=False)
    has_flux_hats = models.BooleanField(default=True)
    dereddening = models.JSONField(null=True, blank=True)
    fluxes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.display_name}"
