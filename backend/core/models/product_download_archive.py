from django.conf import settings
from django.db import models
from django.utils import timezone


class ProductDownloadArchiveStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    RUNNING = "running", "Running"
    READY = "ready", "Ready"
    FAILED = "failed", "Failed"
    EXPIRED = "expired", "Expired"


class ProductDownloadArchive(models.Model):
    product = models.ForeignKey(
        "core.Product",
        on_delete=models.CASCADE,
        related_name="download_archives",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="product_download_archives",
    )
    status = models.CharField(
        max_length=20,
        choices=ProductDownloadArchiveStatus.choices,
        default=ProductDownloadArchiveStatus.PENDING,
    )
    archive_path = models.CharField(max_length=1024, null=True, blank=True)
    filename = models.CharField(max_length=255)
    size = models.BigIntegerField(null=True, blank=True)
    checksum = models.CharField(max_length=64, null=True, blank=True)
    source_signature = models.CharField(max_length=64)
    source_updated_at = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["product", "status"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["source_signature"]),
        ]

    def __str__(self):
        return f"{self.product} - {self.filename} ({self.status})"

    @property
    def is_ready(self):
        return self.status == ProductDownloadArchiveStatus.READY

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= timezone.now()
