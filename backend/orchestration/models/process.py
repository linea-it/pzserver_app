import pathlib
import shutil

from core.models import Product, Release
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from orchestration.models import Pipeline


class ProcessStatus(models.IntegerChoices):
    SUCCESSFUL = 0, "Successful"
    PENDING = 1, "Pending"
    RUNNING = 2, "Running"
    REVOKED = 3, "Revoked"
    FAILED = 4, "Failed"


class Process(models.Model):
    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="processes"
    )
    pipeline_version = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    used_config = models.JSONField(null=True, blank=True)
    inputs = models.ManyToManyField(Product, related_name="processes")
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name="processes",
        null=True,
        blank=True,
        default=None,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="processes")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    status = models.IntegerField(
        verbose_name="Status",
        default=ProcessStatus.PENDING,
        choices=ProcessStatus.choices,
    )
    path = models.FilePathField(
        verbose_name="Path", null=True, blank=True, default=None
    )
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.pk}"

    def delete(self, *args, **kwargs):
        process_path = pathlib.Path(settings.PROCESSING_DIR, str(self.path))
        if process_path.exists():
            self.rmtree(process_path)

        super().delete(*args, **kwargs)

    @staticmethod
    def rmtree(process_path):
        try:
            # WARN: is not run by admin
            shutil.rmtree(process_path)
        except OSError as e:
            raise OSError("Failed to remove directory: [ %s ] %s" % (process_path, e))
