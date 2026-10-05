from types import SimpleNamespace
from unittest import mock

from core.models import Pipeline, Process, Product, ProductStatus, ProductType, Release
from core.process.pipelines.training_set_maker import TrainingSetMakerHandler
from django.contrib.auth.models import User
from django.test import TestCase, override_settings


@override_settings(DATASETS_DIR="/datasets", ORCHEST_URL="http://orchestrator")
class TrainingSetMakerHandlerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "john", "john@snow.com", "you_know_nothing"
        )
        self.product_type = ProductType.objects.create(
            name="redshift_catalog",
            display_name="Redshift Catalog",
        )
        self.pipeline = Pipeline.objects.create(
            name="training_set_maker",
            display_name="Training Set Maker",
            version="1.0.0",
            output_product_type=self.product_type,
        )
        self.upload = Product.objects.create(
            product_type=self.product_type,
            user=self.user,
            display_name="Training Set",
            internal_name="1_training_set",
            path="training_set/1_training_set",
            status=ProductStatus.PROCESSING,
        )
        self.release = Release.objects.create(
            name="dp1",
            display_name="DP1",
            indexing_column="objectId",
            has_mag_hats=True,
            has_flux_hats=True,
            dereddening=[{"name": "sfd", "display_name": "SFD", "selected": True}],
            fluxes=[{"name": "auto", "display_name": "Auto", "selected": True}],
        )

    def test_build_config_uses_release_root_for_dataset_resolution(self):
        process = Process.objects.create(
            display_name="Training Set",
            pipeline=self.pipeline,
            upload=self.upload,
            user=self.user,
            release=self.release,
            used_config={
                "param": {
                    "flux_type": "auto",
                    "dereddening": "sfd",
                    "convert_flux_to_mag": True,
                }
            },
        )

        config = TrainingSetMakerHandler(SimpleNamespace(data={}), process).build_config()

        self.assertEqual("/datasets/dp1", config["inputs"]["dataset"]["path"])
        self.assertEqual(
            {"id": "objectId"},
            config["inputs"]["dataset"]["columns"],
        )
        self.assertEqual(
            {
                "flux_type": "auto",
                "dereddening": "sfd",
                "convert_flux_to_mag": True,
            },
            config["param"],
        )

    @mock.patch("core.process.pipelines.training_set_maker.Maestro")
    def test_build_config_hydrates_hats_config_and_ignores_protected_edits(
        self,
        maestro_class,
    ):
        process = Process.objects.create(
            display_name="Training Set",
            pipeline=self.pipeline,
            upload=self.upload,
            user=self.user,
            release=self.release,
            used_config={
                "param": {
                    "hats_config": {
                        "executor": {"name": "local"},
                        "input": {
                            "catalog_folder": "/tmp/forbidden",
                            "compute_magnitude": False,
                        },
                        "dust": {
                            "path_to_dustmaps": "/tmp/forbidden",
                            "use_dustmap": "planck",
                        },
                    }
                }
            },
        )
        maestro_class.return_value.hats_config.return_value = {
            "release": "dp1",
            "config": {
                "executor": {"name": "slurm"},
                "input": {
                    "catalog_folder": "/datasets/dp1/catalog",
                    "compute_magnitude": True,
                },
                "dust": {
                    "path_to_dustmaps": "/datasets/dustmaps",
                    "use_dustmap": "sfd",
                },
            },
        }

        with self.assertLogs("core.services.hats_config", level="WARNING") as logs:
            config = TrainingSetMakerHandler(
                SimpleNamespace(data={}),
                process,
            ).build_config()

        maestro_class.assert_called_once_with(url="http://orchestrator")
        maestro_class.return_value.hats_config.assert_called_once_with("dp1")
        hats_config = config["param"]["hats_config"]
        self.assertEqual("slurm", hats_config["executor"]["name"])
        self.assertEqual(
            "/datasets/dp1/catalog",
            hats_config["input"]["catalog_folder"],
        )
        self.assertFalse(hats_config["input"]["compute_magnitude"])
        self.assertEqual(
            "/datasets/dustmaps",
            hats_config["dust"]["path_to_dustmaps"],
        )
        self.assertEqual("planck", hats_config["dust"]["use_dustmap"])
        self.assertIn("Ignoring protected HATS configuration fields", logs.output[0])
