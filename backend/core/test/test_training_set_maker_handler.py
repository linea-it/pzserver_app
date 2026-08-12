from types import SimpleNamespace

from core.models import Pipeline, Process, Product, ProductStatus, ProductType, Release
from core.process.pipelines.training_set_maker import TrainingSetMakerHandler
from django.contrib.auth.models import User
from django.test import TestCase, override_settings


@override_settings(DATASETS_DIR="/datasets")
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
            name="dr2",
            display_name="DR2",
            indexing_column="coadd_object_id",
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

        self.assertEqual("/datasets/dr2", config["inputs"]["dataset"]["path"])
        self.assertEqual(
            {"id": "coadd_object_id"},
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
