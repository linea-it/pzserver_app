import logging
import pathlib

from core.models import Product, ProductContent, ProductFile
from core.product_handle import NotTableError, ProductHandle
from core.serializers import ProductSerializer
from django.conf import settings

LOGGER = logging.getLogger("products")


class NonAdminError(ValueError):
    def __init__(self, message):
        LOGGER.debug('Debug: %s', message)
        super().__init__(message)


class CreateProduct:
    def __init__(self, data, user):
        """Create a product with initial information

        Args:
            data (django.http.request.QueryDict): Initial information coming
                from an http request
            user (django.contrib.auth.models.User): User
        """

        LOGGER.debug(f"Creating product: {data}")


        serializer = ProductSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        # initializing product in database
        self.__data = self.__perform_create(serializer, user)

        # checks if the product is official and if the user has permission to add it.
        self.__check_official_product(user)

    def save(self):
        """Save product

        Returns:
            tuple: first position of the tuple reflects the save status, 
                second position is the final message
        """

        # checks if the product fits the business rules of the product type.
        can_save = self.check_product_types()

        if not can_save.get("success"):
            return (False, can_save.get("message"))

        self.__set_internal_name()
        self.__create_product_path()

        LOGGER.debug(f"Product ID {self.__data.pk} created")

        return (True, can_save.get("message"))

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
                raise NonAdminError(
                    "Not allowed. Only users with admin permissions "
                    "can create official products."
                )

        return True

    @property
    def data(self):
        """Product data"""
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
            return {
                "message": {"product": ["No data."]},
                "success": False,
            }

        # Release is not allowed in Spec-z Catalog
        if self.__data.release and self.__data.product_type.name == "specz_catalog":
            self.__delete()
            return {
                "message": {
                    "release": ["Release must be null on Spec-z Catalogs products."]
                },
                "success": False,
            }

        # Pzcode is only allowed in Validations Results and Photo-z Table
        if self.__data.pz_code and self.__data.product_type.name in (
            "training_set",
            "training_results",
            "specz_catalog",
        ):
            dn = self.__data.product_type.display_name
            pzc = self.__data.pz_code
            self.__delete()
            return {
                "message": {
                    "pz_code": [f"Pz Code must be null on {dn} products. '{pzc}'"]
                },
                "success": False,
            }

        return {
            "message": {"product_type": ["Success!"]},
            "success": True,
        }

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

    def __init__(self, product_id):
        self.main_file = None

        LOGGER.debug("Product ID: [%s]" % product_id)
        self.product = Product.objects.get(pk=product_id)
        LOGGER.debug("Internal Name: [%s]" % self.product.internal_name)

    def registry(self):
        """Registry product

        Raises:
            Exception: NotTableError
        """

        try:
            # Alterar o Internal name
            if self.product.internal_name is None:
                self.product.internal_name = (
                    f"{self.product.pk}_{self.product.internal_name}"
                )
                self.product.save()
                LOGGER.debug(
                    "Internal Name Updated to: [%s]" % self.product.internal_name
                )

            # Recupera informação do arquivo principal pela tabela productFile
            mf = self.product.files.get(role=0)
            self.main_file = pathlib.Path(mf.file.path)
            LOGGER.debug("Main File: [%s]" % self.main_file)

            product_columns = list()
            try:
                # Le o arquivo principal e converte para pandas.Dataframe
                df_product = ProductHandle().df_from_file(self.main_file)

                # Lista de Colunas no arquivo.
                product_columns = df_product.columns.tolist()

                # Record number of lines of the main product
                mf.n_rows = len(df_product)
                mf.save()
                LOGGER.debug(f"Number of rows: {str(mf.n_rows)}")
            except NotTableError as err:
                LOGGER.warning(err)
                # Acontece com arquivos comprimidos .zip etc.
                pass

            # Verifica se o product type é specz_catalog
            # Para esses produtos é mandatório ter acesso as colunas da tabela
            # Para os demais produtos é opicional.
            if self.product.product_type.name == "specz_catalog":
                if len(product_columns) == 0:
                    raise Exception((
                        "It was not possible to identify the product columns. "
                        "For Spec-z Catalogs this is mandatory. "
                        "Please check the file format."
                    ))

            # Registra as colunas do produto no banco de dados.
            # é possivel ter produtos sem nenhum registro de coluna
            # Essa regra será tratada no frontend.
            self.create_product_contents(product_columns)
            LOGGER.debug("Created product contents.")

            # Salva as alterações feitas no model product
            self.product.save()

        except Exception as e:
            LOGGER.error(e)
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

            LOGGER.debug(f"{len(columns)} product contents have been registered")

        except Exception as e:
            message = f"Failed to register product content. {e}"
            LOGGER.error(message)
            raise Exception(message)

    def create_product_file(self, filepath, role=0):
        """Create product file

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
            extension=_file.suffix,
        )

        return fileobj.save()
