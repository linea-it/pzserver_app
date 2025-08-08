import pathlib
import shutil

from core.models import Pipeline, Product, Release
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Process(models.Model):
    display_name = models.CharField(max_length=255)
    pipeline = models.ForeignKey(
        Pipeline, on_delete=models.CASCADE, related_name="processes"
    )
    pipeline_version = models.CharField(
        max_length=255, null=True, blank=True, default=None
    )
    used_config = models.JSONField(null=True, blank=True)
    inputs = models.ManyToManyField(Product, related_name="inputs")
    release = models.ForeignKey(
        Release,
        on_delete=models.CASCADE,
        related_name="processes",
        null=True,
        blank=True,
        default=None,
    )
    upload = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="process",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="processes")
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    task_id = models.CharField(max_length=255, null=True, blank=True, default=None)
    orchestration_process_id = models.IntegerField(null=True, blank=True, default=None)
    status = models.CharField(max_length=255, default="Pending")
    path = models.CharField(max_length=255, null=True, blank=True, default=None)
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.pipeline}-{str(self.pk).zfill(8)}"

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
