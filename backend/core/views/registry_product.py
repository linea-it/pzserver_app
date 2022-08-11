import csv
import logging
import os
import shutil
import zipfile
from pathlib import Path

import pandas as pd
from core.models import Product, ProductContent


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

    # def get_path(self):

    #     product_type = self.product.product_type.name

    #     path = Path(
    #         settings.MEDIA_ROOT,
    #         product_type,
    #         self.product.internal_name,
    #     )
    #     path.mkdir(parents=True, exist_ok=True)

    #     self.log.info("Product Path: [%s]" % path)
    #     return path

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

            # Identificar o formato do arquivo principal
            extension = self.main_file.suffix

            match extension:
                case ".csv":
                    self.handle_csv()
                case _:
                    message = f"The {extension} extension has not yet been implemented"
                    self.log.warning(message)
                    raise Exception(message)

            # Salva as alterações feitas no model product
            self.product.save()

        except Exception as e:
            self.log.error(e)
            raise Exception(e)

    def handle_csv(self):
        self.log.info("Using csv format to process main file.")
        csv_file = self.main_file

        # Identificar se o csv tem Headers
        has_header = self.csv_has_header(csv_file)

        columns = list()
        if has_header:
            # Identificar as colunas
            columns = self.csv_column_names(csv_file)
        else:
            # TODO: Implementar função para criar colunas fakes
            pass

        # Registra as colunas do produto no banco de dados:
        self.create_product_contents(columns)

    def csv_has_header(self, path):
        with open(path, "r") as f:
            try:
                has_header = csv.Sniffer().has_header(f.read(2048))
                self.log.info("Has Header: [%s]" % has_header)

                return has_header
            except csv.Error as e:
                message = f"Failed to identify csv headers. {e}"
                self.log.error(message)
                raise Exception(message)

    def csv_identify_delimiter(self, path):
        """Identifica o delimitador e o dialect do csv."""

        with open(path, "r") as f:
            try:
                dialect = csv.Sniffer().sniff(f.read(2048), delimiters=",\t :;")
                delimiter = dialect.delimiter
                self.log.info("Delimiter: [%s]" % delimiter)
                return delimiter
            except csv.Error as e:
                self.log.error(e)
                raise Exception(e)

    def csv_column_names(self, path):

        try:
            # Identificar o Delimitador do csv
            delimiter = self.csv_identify_delimiter(path)

            # Cria um pandas dataframe para recuperar as colunas
            df = pd.read_csv(path, sep=delimiter)
            columns = list(map(str.strip, df.columns))
            self.log.info(f"Columns: {len(columns)}")

            return columns

        except Exception as e:
            message = f"Could not identify csv columns. {e}"
            self.log.error(message)
            raise Exception(message)

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

    def create_zip(self, from_path, to_path, compresslevel=0):
        """
        Comprime um diretorio e seus arquivos para um unico arquivo .zip.
        """
        try:
            self.log.info(f"Compressing the directory: {from_path}")

            with zipfile.ZipFile(
                to_path,
                "w",
                compression=zipfile.ZIP_DEFLATED,
                compresslevel=compresslevel,
            ) as ziphandle:
                for root, dirs, files in os.walk(from_path):
                    for file in files:
                        origin_file = os.path.join(root, file)
                        self.log.debug("Adding File: %s" % origin_file)
                        ziphandle.write(origin_file, arcname=file)

            ziphandle.close()

            self.log.info(f"Compressed directory: {to_path}")

        except Exception as e:
            message = f"Failed to store product files. {e}"
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


# from django.core.files import File
# from django.core.files.base import ContentFile
# from django.conf import settings
# # Criar o path definitivo para o produto
# new_path = self.get_path()
# # TODO: Guardar o path para o diretório no model.

# # Diretório temporario onde foi feito o upload dos arquivos
# temp_dir_path = self.main_file.parent

# # Path para o arquivo zip com todo o conteudo do produto
# zip_name = f"{self.product.internal_name.split('_')[1]}.zip"
# zip_path = Path(new_path, zip_name)

# # Comprimir o diretório e todos os arquivos do produto.
# self.create_zip(temp_dir_path, zip_path, 9)

# # Atualiza o Produto, o main_file agora passa a ser o zip do produto.
# relative_main_file = str(zip_path).split(settings.MEDIA_ROOT)[1]
# self.log.debug(relative_main_file)
# self.product.main_file = relative_main_file
# self.product.save()

# self.product.file_name = zip_path.name
# self.product.file_size = zip_path.stat().st_size
# self.product.file_extension = zip_path.suffix

# # Apaga o diretório temporario
# self.remove_dir(temp_dir_path)
