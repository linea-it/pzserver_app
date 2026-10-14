from core.admin import ReleaseAdmin
from core.models import Release
from django.contrib import admin
from django.test import SimpleTestCase


class ReleaseAdminTestCase(SimpleTestCase):
    def test_data_configuration_has_only_magnitude_conversion_flag(self):
        release_admin = ReleaseAdmin(Release, admin.site)
        data_configuration = dict(release_admin.fieldsets)["Data Configuration"]

        self.assertEqual(
            (
                "can_convert_flux_to_mag",
                "dereddening",
                "fluxes",
            ),
            data_configuration["fields"],
        )

    def test_magnitude_conversion_defaults_to_disabled(self):
        field = Release._meta.get_field("can_convert_flux_to_mag")

        self.assertFalse(field.default)
        self.assertEqual(
            "Allow flux-to-magnitude conversion",
            field.verbose_name,
        )
