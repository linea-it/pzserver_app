from core.models import Pipeline, ProductStatus
from core.product_steps import CreateProduct


class UploadBuilder:

    def __init__(self, serializer, user):
        self.serializer = serializer
        self.user = user

    def build(self):

        data = self.serializer.initial_data
        pipeline = Pipeline.objects.get(pk=data.get("pipeline"))

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

        product.status = ProductStatus.PROCESSING
        product.save()

        return product.data
