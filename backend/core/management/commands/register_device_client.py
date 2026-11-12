from django.core.management.base import BaseCommand, CommandError
from oauth2_provider.models import get_application_model


class Command(BaseCommand):
    help = (
        "Register the public Python client for Device Flow."
    )

    def handle(self, *args, **options):
        model = get_application_model()
        app, _ = model.objects.get_or_create(
            client_id="pzserver-python-device",
            defaults={
                "name": "PzServer Python",
                "client_type": model.CLIENT_PUBLIC,
                "authorization_grant_type": model.GRANT_DEVICE_CODE,
                "skip_authorization": False,
            },
        )
        if (
            app.client_type != model.CLIENT_PUBLIC
            or app.authorization_grant_type != model.GRANT_DEVICE_CODE
            or app.skip_authorization
        ):
            raise CommandError(
                "Existing client has incompatible settings; no changes made."
            )
        self.stdout.write(f"Client ID: {app.client_id}")
