"""Preserve management of Device tokens issued before connected applications."""

import uuid
from django.db import migrations


def import_accesses(apps, schema_editor):
    RefreshToken = apps.get_model("oauth2_provider", "RefreshToken")
    DeviceAccess = apps.get_model("core", "DeviceAccess")
    alias = schema_editor.connection.alias
    tokens = (
        RefreshToken.objects.using(alias)
        .filter(
            application__authorization_grant_type="urn:ietf:params:oauth:grant-type:device_code"
        )
        .select_related("application")
        .only(
            "token_family", "user_id", "application_id", "application__name", "created"
        )
        .order_by("created")
    )
    for token in tokens.iterator():
        if token.token_family is None:
            token.token_family = uuid.uuid4()
            RefreshToken.objects.using(alias).filter(pk=token.pk).update(
                token_family=token.token_family
            )
        access, created = DeviceAccess.objects.using(alias).get_or_create(
            token_family=token.token_family,
            defaults={
                "user_id": token.user_id,
                "application_id": token.application_id,
                "name": (token.application.name or "Python access")[:100],
                "authorized_at": token.created,
            },
        )
        if not created:
            DeviceAccess.objects.using(alias).filter(pk=access.pk).update(
                last_renewed_at=token.created
            )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0066_device_access"),
        ("oauth2_provider", "0022_refreshtoken_token_family_index"),
    ]
    operations = [migrations.RunPython(import_accesses, migrations.RunPython.noop)]
