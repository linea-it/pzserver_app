from django.contrib.auth.models import Group
from django.db import models


class GroupMetadata(models.Model):
    """
    Metadata for Django groups, allowing to differentiate Linea groups from local ones
    and add extra information.
    """

    class GroupSource(models.TextChoices):
        LOCAL = "local", "Local"  # Group created locally in Django
        LINEA = "linea", "LIneA"  # Group created via LIneA IdP

    class Meta:
        verbose_name = "Group Metadata"
        verbose_name_plural = "Group Metadata"

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="metadata",
        help_text="Associated Django group",
    )
    source = models.CharField(
        max_length=10,
        choices=GroupSource.choices,
        default=GroupSource.LOCAL,
        help_text="Group origin",
    )
    display_name = models.CharField(
        max_length=255, blank=True, help_text="Friendly name for display"
    )
    description = models.TextField(blank=True, help_text="Group description")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last synchronization via IdP (only for Linea groups)",
    )

    def __str__(self):
        return f"{self.group.name} ({self.get_source_display()})"

    def save(self, *args, **kwargs):
        # If display_name is empty, use the group name
        if not self.display_name:
            self.display_name = self.group.name
        super().save(*args, **kwargs)

    @property
    def is_linea_group(self):
        """Checks if it's a Linea group."""
        return self.source == self.GroupSource.LINEA

    @property
    def is_local_group(self):
        """Checks if it's a local group."""
        return self.source == self.GroupSource.LOCAL
