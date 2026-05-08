import logging
import pathlib
import time
from json import dumps, loads

from core.models import Product, ProductContent, ProductFile
from core.product_handle import NotTableError
from core.serializers import ProductSerializer
from core.table_data_collector import MainTableDataCollector
from django.conf import settings

LOGGER = logging.getLogger("products")


class NonAdminError(ValueError):
    def __init__(self, message):
        LOGGER.debug("Debug: %s", message)
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

        # Release is not allowed in Redshift Catalog
        if self.__data.release and self.__data.product_type.name == "redshift_catalog":
            self.__delete()
            return {
                "message": {
                    "release": ["Release must be null on Redshift Catalogs products."]
                },
                "success": False,
            }

        # Pzcode is only allowed in Validations Results and Photo-z Table
        if self.__data.pz_code and self.__data.product_type.name in (
            "training_set",
            "training_results",
            "redshift_catalog",
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
    TABLE_PREVIEW_FILENAME = "__table_preview.json"
    TABLE_PREVIEW_PROCESSING_FILENAME = "__table_preview.processing"
    TABLE_PREVIEW_PROCESSING_TTL_SECONDS = 1800
    TABLE_PREVIEW_ROWS = 10
    TABULAR_SUFFIXES = {
        ".csv",
        ".txt",
        ".fits",
        ".fit",
        ".h5",
        ".hf5",
        ".hdf5",
        ".hdf",
        ".parquet",
        ".pq",
    }

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
            table_data = None
            try:
                # Faz uma única leitura dos dados tabulares para reutilizar
                # preview, colunas e número de linhas no registro.
                table_data = self.build_table_preview()
            except NotTableError as err:
                LOGGER.warning(err)
                self.remove_table_preview()

            if table_data:
                product_columns = table_data["columns"]
                if table_data["n_rows"] is not None:
                    mf.n_rows = table_data["n_rows"]
                    mf.save(update_fields=["n_rows", "updated"])
                    LOGGER.debug("Number of rows: %s", str(mf.n_rows))

            # Verifica se o product type é redshift_catalog
            # Para esses produtos é mandatório ter acesso as colunas da tabela
            # Para os demais produtos é opicional.
            if self.product.product_type.name == "redshift_catalog":
                if len(product_columns) == 0:
                    raise Exception(
                        (
                            "It was not possible to identify the product columns. "
                            "For Redshift Catalogs this is mandatory. "
                            "Please check the file format."
                        )
                    )

            # Registra as colunas do produto no banco de dados.
            # é possivel ter produtos sem nenhum registro de coluna
            # Essa regra será tratada no frontend.

            product_columns = {v: dict() for v in product_columns}

            self.create_product_contents(product_columns)
            LOGGER.debug("Created product contents.")

            # Salva as alterações feitas no model product
            self.product.save()

        except Exception as e:
            LOGGER.error(e)
            raise Exception(e)

    @classmethod
    def get_table_preview_path(cls, product):
        """Build the absolute path to the cached table preview JSON file."""
        return pathlib.Path(settings.MEDIA_ROOT, product.path, cls.TABLE_PREVIEW_FILENAME)

    @classmethod
    def get_table_preview_processing_path(cls, product):
        """Build the absolute path to the table preview processing marker file."""
        return pathlib.Path(
            settings.MEDIA_ROOT, product.path, cls.TABLE_PREVIEW_PROCESSING_FILENAME
        )

    @classmethod
    def start_table_preview_processing(cls, product):
        """Create a processing marker atomically.

        Returns:
            bool: True if this call created the marker, False if it already exists.
        """
        processing_path = cls.get_table_preview_processing_path(product)
        try:
            with processing_path.open("x", encoding="utf-8") as marker:
                marker.write(str(time.time()))
            return True
        except FileExistsError:
            return False

    @classmethod
    def stop_table_preview_processing(cls, product):
        """Remove the table preview processing marker file."""
        processing_path = cls.get_table_preview_processing_path(product)
        processing_path.unlink(missing_ok=True)

    @classmethod
    def is_table_preview_processing(cls, product):
        """Check whether preview generation is currently in progress.

        A stale marker older than TABLE_PREVIEW_PROCESSING_TTL_SECONDS is
        automatically removed.
        """
        processing_path = cls.get_table_preview_processing_path(product)
        if not processing_path.exists():
            return False

        age = time.time() - processing_path.stat().st_mtime
        if age > cls.TABLE_PREVIEW_PROCESSING_TTL_SECONDS:
            processing_path.unlink(missing_ok=True)
            return False
        return True

    def remove_table_preview(self):
        """Delete any existing cached table preview file for the product."""
        preview_path = self.get_table_preview_path(self.product)
        preview_path.unlink(missing_ok=True)

    def _load_main_file(self):
        """Load and cache the absolute path of the product main file."""
        if self.main_file is None:
            main_file = self.product.files.get(role=0)
            self.main_file = pathlib.Path(main_file.file.path)
            LOGGER.debug("Main File: [%s]" % self.main_file)
        return self.main_file

    def build_table_preview(self):
        """Collect tabular metadata and update the preview cache.

        Returns:
            dict: Table metadata with keys `preview_df`, `columns`, and `n_rows`.
        """
        main_file = self._load_main_file()
        collector = MainTableDataCollector(
            main_file=main_file,
            preview_rows=self.TABLE_PREVIEW_ROWS,
            tabular_suffixes=self.TABULAR_SUFFIXES,
        )
        table_data = collector.collect()
        self.create_table_preview(table_data["preview_df"])
        return table_data

    def create_table_preview(self, df_preview):
        """Persist the table preview payload to a JSON file.

        Args:
            df_preview (pandas.DataFrame): DataFrame containing preview rows.
        """
        payload = {
            "count": int(df_preview.shape[0]),
            "columns": list(df_preview.columns),
            "results": loads(df_preview.to_json(orient="records")),
        }
        preview_path = self.get_table_preview_path(self.product)
        preview_path.write_text(dumps(payload), encoding="utf-8")
        LOGGER.debug("Table preview generated: %s", preview_path)

    def create_product_contents(self, columns):
        """Registrar as colunas na tabela Product Contents

        Args:
            columns (dict): columns mapping
        """
        try:
            cached_ucds = dict()

            # Remove todas as colunas caso exista
            for col in self.product.contents.all():
                # Caso a coluna tenha valor de UCD esse sera mantido ao recriar a coluna com mesmo nome
                cached_ucds[col.column_name] = {"ucd": col.ucd, "alias": col.alias}
                col.delete()

            for idx, column_name in enumerate(columns):
                ucd = columns.get(column_name, {}).get("ucd", None)
                alias = columns.get(column_name, {}).get("alias", None)

                if column_name in cached_ucds and not ucd and not alias:
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

    def create_product_file(self, filepath, relative_path, role=0):
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
            file=relative_path,
            product_id=self.product.pk,
            extension=_file.suffix,
        )

        return fileobj.save()
