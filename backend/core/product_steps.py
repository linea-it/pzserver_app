import logging
import pathlib

from core.models import Product, ProductContent, ProductFile
from core.product_handle import NotTableError, ProductHandle
from core.serializers import ProductSerializer
from django.conf import settings
from rest_framework.reverse import reverse


class CreateProduct:
    
    def __init__(self, data, user):
        """ Create a product with initial information

        Args:
            data (django.http.request.QueryDict): Initial information coming 
                from an http request
            user (django.contrib.auth.models.User): User 
        """

        self.__log = logging.getLogger("products")
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

    def __perform_create(self, serializer, user) -> ProductSerializer:
        """Add user"""

        uploaded_by = user
        return serializer.save(user=uploaded_by)
    
    def __delete(self):
        """Delete product"""

        if self.__data:
            self.__data.path = f"{settings.MEDIA_ROOT}/{self.__data.path}"
            self.__data.delete()
            self.__data = None


class RegistryProduct:
    log = None

    def __init__(self, product_id):
        self.log = self.get_log()
        self.main_file = None

        self.log.info("----------------------------")
        self.log.info("Product ID: [%s]" % product_id)
        self.product = Product.objects.get(pk=product_id)
        self.log.info("Internal Name: [%s]" % self.product.internal_name)

    def get_log(self):
        if not self.log:
            # Get an instance of a logger
            self.log = logging.getLogger("products")
        return self.log

    def registry(self):
        try:
            # Alterar o Internal name
            if self.product.internal_name is None:
                self.product.internal_name = (
                    f"{self.product.pk}_{self.product.internal_name}"
                )
                self.product.save()
                self.log.info(
                    "Internal Name Updated to: [%s]" % self.product.internal_name
                )

            # Recupera informação do arquivo principal
            # pela tabela productFile
            mf = self.product.files.get(role=0)
            self.main_file = pathlib.Path(mf.file.path)
            self.log.info("Main File: [%s]" % self.main_file)

            product_columns = list()
            try:
                # Le o arquivo principal e converte para pandas.Dataframe
                df_product = ProductHandle().df_from_file(self.main_file, nrows=5)
                # Lista de Colunas no arquivo.
                product_columns = df_product.columns.tolist()
            except NotTableError:
                # Acontece com arquivos comprimidos .zip etc.
                pass

            # Verifica se o product type é specz_catalog
            # Para esses produtos é mandatório ter acesso as colunas da tabela
            # Para os demais produtos é opicional.
            if self.product.product_type.name == "specz_catalog":
                if len(product_columns) == 0:
                    raise Exception(
                        "It was not possible to identify the product columns. for Spec-z Catalogs this is mandatory. Please check the file format."
                    )

            # Registra as colunas do produto no banco de dados.
            # é possivel ter produtos sem nenhum registro de coluna
            # Essa regra será tratada no frontend.
            self.create_product_contents(product_columns)

            # Salva as alterações feitas no model product
            self.product.save()

        except Exception as e:
            self.log.error(e)
            raise Exception(e)

    def create_product_contents(self, columns):
        """Registrar as colunas na tabela Product Contents

        Args:
            columns (_type_): _description_
        """
        try:
            cached_ucds = dict()

            # Remove todas as colunas caso exista
            for col in self.product.contents.all():
                # Caso a coluna tenha valor de UCD esse sera mantido ao recriar a coluna com mesmo nome
                cached_ucds[col.column_name] = {"ucd": col.ucd, "alias": col.alias}
                col.delete()

            for idx, column_name in enumerate(columns):
                ucd = None
                alias = None
                if column_name in cached_ucds:
                    ucd = cached_ucds[column_name]["ucd"]
                    alias = cached_ucds[column_name]["alias"]

                ProductContent.objects.create(
                    product=self.product,
                    column_name=column_name,
                    order=idx,
                    ucd=ucd,
                    alias=alias,
                )

            self.log.info(f"{len(columns)} product contents have been registered")

        except Exception as e:
            message = f"Failed to register product content. {e}"
            self.log.error(message)
            raise Exception(message)

    def create_product_file(self, filepath, role=0):
        """ Create product file

        Args:
            filepath (str): Product path
        """

        _file = pathlib.Path(filepath)
        
        fileobj = ProductFile(
            name=_file.name,
            role=role,
            product=self.product,
            size=_file.stat().st_size,
            file=str(_file),
            product_id=self.product.pk,
            extension=_file.suffix
        )

        return fileobj.save()
        