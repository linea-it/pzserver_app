import logging
import shutil
from pathlib import Path

from core.models import Product, ProductContent
from core.product_handle import ProductHandle


class RegistryProduct:

    log = None
    product = None
    main_file = None

    def __init__(self, product_id):
        self.log = self.get_log()

        self.log.info("----------------------------")
        self.log.info("Product ID: [%s]" % product_id)

        self.product = Product.objects.get(pk=product_id)

        self.log.info("Internal Name: [%s]" % self.product.internal_name)

    def get_log(self):
        if not self.log:
            # Get an instance of a logger
            self.log = logging.getLogger("registry_product")
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
            self.main_file = Path(mf.file.path)
            self.log.info("Main File: [%s]" % self.main_file)

            # Le o arquivo principal e converte para pandas.Dataframe
            df_product = ProductHandle().df_from_file(self.main_file, nrows=5)
            # Lista de Colunas no arquivo.
            product_columns = df_product.columns.tolist()
            # Registra as colunas do produto no banco de dados.
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
                cached_ucds[col.column_name] = col.ucd
                col.delete()

            for idx, column_name in enumerate(columns):

                ucd = None
                if column_name in cached_ucds:
                    ucd = cached_ucds[column_name]

                ProductContent.objects.create(
                    product=self.product,
                    column_name=column_name,
                    order=idx,
                    ucd=ucd,
                )

            self.log.info(f"{len(columns)} product contents have been registered")

        except Exception as e:
            message = f"Failed to register product content. {e}"
            self.log.error(message)
            raise Exception(message)

    def remove_dir(self, path):
        try:
            shutil.rmtree(path)
            self.log.info(f"Directory removed: [{path}]")
        except Exception as e:
            message = f"Failed to register the product. {e}"
            self.log.error(message)
            raise Exception(message)
