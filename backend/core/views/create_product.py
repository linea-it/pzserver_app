import logging
import pathlib

from core.models import Product
from core.serializers import ProductSerializer
from django.conf import settings


class CreateProduct:
    
    def __init__(self, data, user):
        self.__log = logging.getLogger("create_product")
        self.__log.debug(f"Creating product: {data}")

        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.__data = self.__perform_create(serializer, user)
        self.__check_official_product(user)

    def save(self):
        can_save = self.check_product_types()

        if not can_save.get("success"):
            return can_save.get("message")

        self.__set_internal_name()
        self.__create_product_path()

        self.__log.debug(f"Product ID {self.__data.pk} created")

    def __check_official_product(self, user):
        """Checks if the product is official and if the user has permission 
        to save an official product.

        Args:
            user (User): User object

        Raises:
            ValueError: if the user no has permission

        Returns:
            bool
        """

        is_official = self.__data.official_product

        if is_official:
            if user.profile.is_admin() is False:
                self.__delete()
                raise ValueError(
                    "Not allowed. Only users with admin permissions "
                    "can create official products."
                )
            
        return True

    @property
    def data(self):
        return self.__data

    def get(self):
        """Returns Product object

        Returns:
            Product object
        """
        return Product.objects.get(pk=self.__data.pk)

    def __set_internal_name(self):
        """Sets the internal name based on the primary key and display name"""

        # change spaces to "_", convert to lowercase, remove trailing spaces.
        name = self.__data.display_name.replace(" ", "_").lower().strip().strip("\n")

        # strip any non-alphanumeric character except "_"
        name = "".join(e for e in name if e.isalnum() or e == "_")
        self.__data.internal_name = f"{self.__data.pk}_{name}"
        self.__data.save()

    def __create_product_path(self):
        """Create product path"""

        # Create product path
        relative_path = f"{self.__data.product_type.name}/{self.__data.internal_name}"
        path = pathlib.Path(settings.MEDIA_ROOT, relative_path)
        path.mkdir(parents=True, exist_ok=True)

        self.__data.path = relative_path
        self.__data.save()

    def check_product_types(self):
        """Checks product types by applying a certain business rule.

        Returns:
            dict: {'message': {'entity':list(str)}, 'status': bool} 
        """

        if not self.__data:
            return {"message": {"product": ["No data."]}, "success": False,}

        # Release is not allowed in Spec-z Catalog
        if (
            self.__data.release
            and self.__data.product_type.name == "specz_catalog"
        ):
            self.__delete()
            return {
                "message": {"release": [
                    "Release must be null on Spec-z Catalogs products."
                ]}, "success": False,
            }

        # Pzcode is only allowed in Validations Results and Photo-z Table
        if self.__data.pz_code and self.__data.product_type.name in (
            "training_set",
            "specz_catalog",
        ):
            dn = self.__data.product_type.display_name
            pzc = self.__data.pz_code
            self.__delete()
            return {
                "message": {"pz_code": [
                    f"Pz Code must be null on {dn} products. '{pzc}'"
                ]}, "success": False,
            }
        
        return {"message": {"product_type": ["Success!"]}, "success": True,}

    def __perform_create(self, serializer, user):
        """Add user"""

        uploaded_by = user
        return serializer.save(user=uploaded_by)
    
    def __delete(self):
        """Delete product"""

        if self.__data:
            self.__data.path = f"{settings.MEDIA_ROOT}/{self.__data.path}"
            self.__data.delete()
            self.__data = None













