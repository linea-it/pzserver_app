"""Database-backed limits shared by all API workers (no raw IPs stored)."""

import math
from datetime import timedelta
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.crypto import salted_hmac
from core.models import DeviceRateLimit


def consume(bucket, identity, limit, seconds):
    key = salted_hmac(
        "device-rate-limit", f"{bucket}:{identity}", algorithm="sha256"
    ).hexdigest()
    with transaction.atomic():
        DeviceRateLimit.objects.get_or_create(key=key)
        row = DeviceRateLimit.objects.select_for_update().get(key=key)
        now = timezone.now()
        if now >= row.started_at + timedelta(seconds=seconds):
            row.started_at, row.count = now, 0
        if row.count >= limit:
            return max(
                1,
                math.ceil(
                    (row.started_at + timedelta(seconds=seconds) - now).total_seconds()
                ),
            )
        row.count += 1
        row.save(update_fields=["started_at", "count"])
    return 0


def limited_response(wait):
    response = JsonResponse(
        {
            "error": "slow_down",
            "error_description": "Too many attempts. Try again later.",
        },
        status=429,
    )
    response["Retry-After"] = str(wait)
    response["Cache-Control"] = "no-store"
    response["Pragma"] = "no-cache"
    return response
