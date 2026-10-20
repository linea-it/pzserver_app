import json
import os

from core.hub_urls import normalize_hub_url
from core.models import TrustedJupyterHub
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


class Command(BaseCommand):
    help = "Import legacy JUPYTERHUB_PARTNERS_JSON once, without overwriting existing Hubs."

    @transaction.atomic
    def handle(self, *args, **options):
        try:
            config = json.loads(os.environ.get("JUPYTERHUB_PARTNERS_JSON", "{}"))
            if not isinstance(config, dict):
                raise ValueError("Expected a JSON object keyed by public URL.")
            created = 0
            for url, values in config.items():
                canonical = normalize_hub_url(url)
                if TrustedJupyterHub.objects.filter(public_url=canonical).exists():
                    continue
                TrustedJupyterHub.objects.create(
                    name=values.get("name", canonical),
                    public_url=canonical,
                    aliases=values.get("aliases", []),
                    user_url=values["user_url"],
                    enabled=values.get("enabled") is True,
                )
                created += 1
        except (
            ValueError,
            TypeError,
            KeyError,
            AttributeError,
            ValidationError,
        ) as exc:
            raise CommandError(
                "Invalid Hub configuration; import rolled back."
            ) from exc
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created} Hub(s). Existing records unchanged."
            )
        )
