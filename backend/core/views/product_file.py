import logging
import os

from core.models import Product, ProductFile
from core.serializers import ProductFileSerializer
from rest_framework import exceptions, mixins, status, viewsets
from rest_framework.response import Response

logger = logging.getLogger("django")


class ProductFileViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ProductFile.objects.all()
    serializer_class = ProductFileSerializer
    filterset_fields = ("id", "product_id")
    ordering_fields = ["id", "role"]
    ordering = ["id"]

    def create(self, request):

        logger.debug("Creating product file")
        logger.debug(request.data)

        product_id = request.data.get("product")
        product = Product.objects.get(id=product_id)

        if product.user.id == request.user.id:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instance = self.perform_create(serializer)

            data = self.get_serializer(instance=instance).data
            return Response(data, status=status.HTTP_201_CREATED)

        return Response(
            {"detail": "You do not have permission to perform this action."},
            status=status.HTTP_403_FORBIDDEN,
        )

    def perform_create(self, serializer):
        """Add size, name and extension."""

        file = self.request.data.get("file")
        size = file.size
        filename, extension = os.path.splitext(file.name)

        return serializer.save(
            size=size,
            name=file.name,
            extension=extension,
        )

    def destroy(self, request, pk=None, *args, **kwargs):
        """Product can only be deleted by the OWNER or if the user has an
        admin profile.
        """

        instance = self.get_object()
        if instance.can_delete(self.request.user):
            return super(ProductFileViewSet, self).destroy(request, pk, *args, **kwargs)
        else:
            raise exceptions.PermissionDenied()
