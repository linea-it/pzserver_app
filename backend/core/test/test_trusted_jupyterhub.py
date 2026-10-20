import json
from io import StringIO
from unittest.mock import patch

from core.models import TrustedJupyterHub
from django.core.exceptions import ValidationError
from django.core.management import CommandError, call_command
from django.test import TestCase


class TrustedHubTests(TestCase):
    def create(self, **kwargs):
        data = dict(
            name="Hub",
            public_url="https://hub.example",
            user_url="https://hub.example/hub/api/user",
        )
        data.update(kwargs)
        return TrustedJupyterHub.objects.create(**data)

    def test_normalization_and_default_disabled(self):
        hub = self.create(
            public_url="https://HUB.example:443/",
            aliases=["https://alias.example/prefix/"],
        )
        hub.refresh_from_db()
        self.assertEqual(hub.public_url, "https://hub.example")
        self.assertEqual(hub.aliases, ["https://alias.example/prefix"])
        self.assertFalse(hub.enabled)

    def test_global_alias_conflicts(self):
        self.create(aliases=["https://alias.example/"])
        for data in (
            dict(public_url="https://ALIAS.example:443"),
            dict(public_url="https://other.example", aliases=["https://hub.example/"]),
            dict(public_url="https://other.example", aliases=["https://alias.example"]),
        ):
            with self.assertRaises(ValidationError):
                self.create(**data)

    def test_invalid_fields(self):
        for data in (
            dict(user_url="http://hub.example/api"),
            dict(aliases="https://alias.example"),
            dict(aliases=["https://hub.example/"]),
            dict(aliases=[123]),
        ):
            with self.assertRaises(ValidationError):
                self.create(**data)

    def test_import_is_idempotent_and_does_not_overwrite(self):
        config = {
            "https://hub.example/": {
                "enabled": True,
                "user_url": "https://hub.example/hub/api/user",
            }
        }
        with patch.dict("os.environ", JUPYTERHUB_PARTNERS_JSON=json.dumps(config)):
            call_command("import_jupyterhubs", stdout=StringIO())
            hub = TrustedJupyterHub.objects.get()
            hub.enabled = False
            hub.save()
            call_command("import_jupyterhubs", stdout=StringIO())
        self.assertEqual(TrustedJupyterHub.objects.count(), 1)
        hub.refresh_from_db()
        self.assertFalse(hub.enabled)

    def test_import_rolls_back_if_any_record_is_invalid(self):
        config = {
            "https://hub.example": {"user_url": "https://hub.example/api"},
            "bad": {},
        }
        with patch.dict("os.environ", JUPYTERHUB_PARTNERS_JSON=json.dumps(config)):
            with self.assertRaises(CommandError):
                call_command("import_jupyterhubs", stdout=StringIO())
        self.assertFalse(TrustedJupyterHub.objects.exists())

    def test_admin_model_form_reports_conflict_before_save(self):
        from django.forms import modelform_factory

        self.create(aliases=["https://alias.example"])
        form_class = modelform_factory(
            TrustedJupyterHub,
            fields=["name", "public_url", "aliases", "user_url", "enabled"],
        )
        form = form_class(
            data={
                "name": "Other",
                "public_url": "https://other.example",
                "aliases": '["https://alias.example/"]',
                "user_url": "https://other.example/api",
                "enabled": True,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("aliases", form.errors)
