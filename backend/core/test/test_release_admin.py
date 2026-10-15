from core.admin import ReleaseAdmin
from core.models import Release
from django.contrib import admin
from django.test import SimpleTestCase


class ReleaseAdminTestCase(SimpleTestCase):
    def test_data_configuration_includes_tsm_availability(self):
        release_admin = ReleaseAdmin(Release, admin.site)
        data_configuration = dict(release_admin.fieldsets)["Data Configuration"]

        self.assertEqual(
            (
                "is_tsm_available",
                "can_convert_flux_to_mag",
                "dereddening",
                "fluxes",
            ),
            data_configuration["fields"],
        )

    def test_tsm_availability_defaults_to_enabled(self):
        field = Release._meta.get_field("is_tsm_available")

        self.assertTrue(field.default)
        self.assertEqual("Available in Training Set Maker", field.verbose_name)

    def test_magnitude_conversion_defaults_to_disabled(self):
        field = Release._meta.get_field("can_convert_flux_to_mag")

        self.assertFalse(field.default)
        self.assertEqual(
            "Allow flux-to-magnitude conversion",
            field.verbose_name,
        )
