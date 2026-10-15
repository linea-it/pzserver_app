from core.models import Release
from django.test import TestCase


class InitialDp1FixtureTestCase(TestCase):
    fixtures = ["core/fixtures/initial_data.yaml"]

    def test_dp1_is_the_only_initial_release(self):
        self.assertEqual(1, Release.objects.count())

        release = Release.objects.get(name="dp1")
        self.assertEqual(1, release.pk)
        self.assertEqual("objectId", release.indexing_column)
        self.assertTrue(release.is_tsm_available)
        self.assertTrue(release.can_convert_flux_to_mag)
        self.assertEqual(
            [{"name": "cModel", "display_name": "cModel", "selected": True}],
            release.fluxes,
        )
        self.assertEqual(
            [{"name": "none", "display_name": "None", "selected": True}],
            release.dereddening,
        )
        self.assertTrue(release.is_public)
