import uuid
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0067_import_device_accesses"),
        ("oauth2_provider", "0022_refreshtoken_token_family_index"),
    ]
    operations = [
        migrations.CreateModel(
            name="DeviceRateLimit",
            fields=[
                (
                    "key",
                    models.CharField(max_length=64, primary_key=True, serialize=False),
                ),
                (
                    "started_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now, db_index=True
                    ),
                ),
                ("count", models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="DeviceAuthorizationAttempt",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("errors", models.PositiveSmallIntegerField(default=0)),
                (
                    "grant",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="oauth2_provider.devicegrant",
                    ),
                ),
            ],
        ),
    ]
