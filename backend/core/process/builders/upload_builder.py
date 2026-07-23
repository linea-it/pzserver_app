import logging

from core.models import Pipeline, ProductStatus
from core.product_steps import CreateProduct


LOGGER = logging.getLogger("django")


class UploadBuilder:

    def __init__(self, serializer, user):
        self.serializer = serializer
        self.user = user

    def build(self):

        data = self.serializer.initial_data
        pipeline = Pipeline.objects.get(pk=data.get("pipeline"))
        LOGGER.info(
            "Creating pipeline upload product pipeline_id=%s pipeline_name=%s user_id=%s display_name=%s release_id=%s",
            pipeline.pk,
            pipeline.name,
            self.user.pk,
            data.get("display_name"),
            data.get("release"),
        )

        upload_data = {
            "display_name": data.get("display_name"),
            "release": data.get("release"),
            "pz_code": data.get("pz_code"),
            "official_product": data.get("official_product", False),
            "description": data.get("description"),
            "product_type": pipeline.output_product_type.pk,
        }

        product = CreateProduct(upload_data, self.user)
        check = product.check_product_types()

        if not check.get("success"):
            raise ValueError(check.get("message"))

        created_product = product.data
        LOGGER.info(
            "Product status transition product_id=%s process_id=%s old_status=%s new_status=%s reason=%s",
            created_product.pk,
            None,
            ProductStatus(created_product.status).label,
            ProductStatus(ProductStatus.PROCESSING).label,
            "pipeline_upload_created",
        )
        created_product.status = ProductStatus.PROCESSING
        product.save()
        LOGGER.info(
            "Created pipeline upload product product_id=%s pipeline_id=%s status=%s path=%s",
            created_product.pk,
            pipeline.pk,
            ProductStatus(created_product.status).label,
            created_product.path,
        )

        return created_product
