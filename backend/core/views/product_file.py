import logging
import os

from core.models import FileRoles, FileStorageKind, Product, ProductFile
from core.serializers import ProductFileSerializer
from core.services.hats_collection import (
    HatsArchiveError,
    NotHatsCollectionError,
    UnsafeArchiveError,
    is_hats_archive_name,
    product_type_accepts_hats,
    validate_and_store_hats_archive,
    validate_hats_archive,
)
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
        _, extension = os.path.splitext(file.name)

        if file.name.lower().endswith(".tar.gz"):
            extension = ".tar.gz"
        elif file.name.lower().endswith(".tgz"):
            extension = ".tgz"

        product = serializer.validated_data["product"]
        role = serializer.validated_data.get("role", FileRoles.MAIN)

        if role == FileRoles.MAIN and is_hats_archive_name(file.name):
            if product_type_accepts_hats(product.product_type.name):
                try:
                    relative_path, metadata = validate_and_store_hats_archive(
                        file, product
                    )
                    return serializer.save(
                        file=relative_path,
                        size=size,
                        name=file.name,
                        extension=extension,
                        storage_kind=FileStorageKind.HATS_COLLECTION,
                        metadata=metadata,
                        n_rows=metadata.get("n_rows"),
                    )
                except NotHatsCollectionError:
                    file.seek(0)
                except (HatsArchiveError, UnsafeArchiveError) as exc:
                    raise exceptions.ValidationError({"error": str(exc)}) from exc
            else:
                try:
                    validate_hats_archive(file)
                except NotHatsCollectionError:
                    file.seek(0)
                except (HatsArchiveError, UnsafeArchiveError) as exc:
                    raise exceptions.ValidationError({"error": str(exc)}) from exc
                else:
                    raise exceptions.ValidationError(
                        {
                            "error": (
                                "HATS collections are not accepted for "
                                f"{product.product_type.display_name} products."
                            )
                        }
                    )

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
