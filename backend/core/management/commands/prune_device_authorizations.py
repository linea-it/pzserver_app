from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from oauth2_provider.models import get_device_grant_model
from core.models import DeviceRateLimit


class Command(BaseCommand):
    help = "Remove expired temporary Device grants and old rate-limit counters."

    def handle(self, *args, **options):
        now = timezone.now()
        get_device_grant_model().objects.filter(expires__lt=now).delete()
        retention = settings.PZSERVER_DEVICE_RATE_LIMIT_RETENTION_SECONDS
        DeviceRateLimit.objects.filter(
            started_at__lt=now - timedelta(seconds=retention)
        ).delete()
        self.stdout.write("Expired Device requests and old counters removed.")
