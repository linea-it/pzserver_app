import abc
import csv
from collections import OrderedDict
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
import tables_io
from core._typing import Column, PathLike


class NotTableError(TypeError):
    pass


class ProductHandle:
    def df_from_file(self, filepath: PathLike, **kwargs) -> pd.DataFrame:
        """TODO: Descrever essa função
        OBS: é possivel utilizar todos os argumentos da função pandas.read_csv()
        descritos aqui: https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html

        Args:
            filepath (PathLike): _description_

        Returns:
            pd.DataFrame: _description_
        """
        return FileHandle(filepath).to_df(**kwargs)


class FileHandle(object):
    handle = None
    extension = None

    def __init__(self, filepath: PathLike):
        fp = Path(filepath)

        # Identificar o formato do arquivo
        self.extension = fp.suffix

        # Instancia o Handle de acordo com o tipo de arquivo
        match self.extension:
            case ".csv":
                self.handle = CsvHandle(fp)
            case ".fits" | ".fit" | ".hf5" | ".hdf5" | ".h5" | ".pq" | ".parquet":
                self.handle = TableIOHandle(fp)
            case ".zip" | ".tar" | ".gz":
                self.handle = CompressedHandle(fp)
            # TODO: .zip, .tar, .tar.gz
            case _:
                # Try TxtHandle
                self.handle = TxtHandle(fp)
                # message = f"The {self.extension} extension has not yet been implemented"
                # raise NotImplementedError(message)

    def to_df(self, **kwargs):
        return self.handle.to_df(**kwargs)


class BaseHandle(object):
    filepath = None

    def __init__(self, filepath: PathLike):
        self.filepath = filepath

    @abc.abstractmethod
    def to_df(self, **kwargs) -> pd.DataFrame:
        raise NotImplementedError


class CsvHandle(BaseHandle):
    delimiter = str
    has_hd = bool  # True se o arquivo CSV possuir Headers na primeira linha.
    # Lista com nome das colunas que podem ser str ou int.
    column_names = [Column]

    def __init__(self, filepath: PathLike):
        super().__init__(filepath)

        self.delimiter = self.get_delimiter()
        self.has_hd = self.has_header()
        self.column_names = self.get_column_names()

    def to_df(self, **kwargs) -> pd.DataFrame:
        # Check for header parameter
        if "header" in kwargs:
            raise Exception(
                "It is not possible to use the header argument in the df_from_file() method when the file is a .csv file."
            )

        if "delimiter" in kwargs:
            raise Exception(
                "It is not possible to use the delimiter argument in the df_from_file() method when the file is a .csv file."
            )

        if self.has_hd:
            df = pd.read_csv(
                self.filepath, header=0, delimiter=self.delimiter, **kwargs
            )
        else:
            df = pd.read_csv(
                self.filepath,
                header=None,
                names=self.column_names,
                delimiter=self.delimiter,
                **kwargs,
            )
        return df

    def has_header(self) -> bool:
        """Verifica se o csv tem Header.
        Usa dois metodos diferentes para checar.
        - vai considerar que tem Header se tiver pelo menos uma coluna como string.
        - vai considerar que tem Header se os tipos de dados forem diferentes na primeira linha.
        - Retorna True se ambos os metodos retornarem True.
        - Retorna False se um dos metodos retornar False.
        Args:
            path (_type_): _description_

        Returns:
            bool: True se o csv possuir Headers na primeira linha.
        """
        temp = []

        # Method: open csv twice considering with header and without header,
        # if the data types are the same in both times it probably doesn't have header.
        # https://stackoverflow.com/questions/53100598/can-pandas-auto-recognize-if-header-is-present/53101192#53101192
        df = pd.read_csv(self.filepath, header=None, delimiter=self.delimiter, nrows=20)
        df_header = pd.read_csv(self.filepath, delimiter=self.delimiter, nrows=20)
        if tuple(df.dtypes) != tuple(df_header.dtypes):
            temp.append(True)
        else:
            temp.append(False)

        # Method: Check if at least one in first Line is String.
        # https://stackoverflow.com/questions/38360496/pandas-read-csv-without-knowing-whether-header-is-present/62217716#62217716
        if any(df.iloc[0].apply(lambda x: isinstance(x, str))):
            temp.append(True)
        else:
            temp.append(False)
        return all(temp)

    def get_column_names(self) -> List[Column]:
        df = pd.read_csv(self.filepath, header=None, delimiter=self.delimiter, nrows=5)

        if self.has_hd:
            df = df[1:].reset_index(drop=True).rename(columns=df.iloc[0])
            columns = df.columns.tolist()
        else:
            # Cria nomes para as colunas de forma sequencial [0...len(headers)]
            # o Resultado é uma lista de str: ['0', ...,'10',...]
            columns = [str(i) for i in [*range(0, len(df.iloc[0]))]]

        return columns

    def get_delimiter(self):
        """Get delimiter from file

        Returns:
            str: delimiter
        """
        with open(self.filepath, "r") as csvfile:
            dt = csvfile.readline().replace("\n", "")
            delimiter = csv.Sniffer().sniff(dt).delimiter

        return delimiter


class TableIOHandle(BaseHandle):
    def __init__(self, filepath: PathLike):
        super().__init__(filepath)

    def to_df(self, **kwargs) -> pd.DataFrame:
        # Le o arquivo utilizando o metodo read da tables_io
        # O retorno é um astropy table.
        df = tables_io.read(self.filepath, tables_io.types.AP_TABLE)

        # TODO: Tratar arquivos com mais de uma tabela.
        if isinstance(df, OrderedDict):
            df = df[list(df.keys())[0]]

        # Converte o astropy table para pandas.Dataframe
        try:
            df = df.to_pandas()
        except ValueError as _:
            df = tables_io.read(self.filepath, tables_io.types.PD_DATAFRAME)

        return df


class CompressedHandle(BaseHandle):
    def __init__(self, filepath: PathLike):
        super().__init__(filepath)

    def to_df(self, **kwargs) -> pd.DataFrame:
        raise NotTableError(
            "It is not possible to return a dataframe from this file type."
        )


class TxtHandle(BaseHandle):
    delimiter = str
    has_hd = bool
    skiprows = int
    # Lista com nome das colunas que podem ser str ou int.
    column_names = [Column]

    def __init__(self, filepath: PathLike):
        super().__init__(filepath)

        self.delimiter = self.get_delimiter()

        self.delim_whitespace = False
        if self.delimiter == None:
            self.delim_whitespace = True

        self.skiprows = self.count_skiprows()

        self.has_hd = self.has_header()

        self.column_names = self.get_column_names()

    def to_df(self, **kwargs) -> pd.DataFrame:
        # Try read table using numpy
        # Ignore all lines start with #
        # ignores all initial lines that after the split have only string.
        # Acept space as delimiter.
        # Does not accept string values.
        df = pd.read_csv(
            self.filepath,
            delimiter=self.delimiter,
            skiprows=self.skiprows,
            names=self.column_names,
            header=None,
            delim_whitespace=self.delim_whitespace,
        )
        return df

    def has_header(self) -> bool:
        if self.skiprows == 1:
            return True
        else:
            return False

    def get_column_names(self) -> List[Column]:
        # Tenta ler o nome das colunas apenas para arquivos onde a primeira linha é toda de string.
        if self.has_hd:
            with open(self.filepath, "r") as fp:
                line = fp.readline().replace("\r\n", "")
                if line.startswith("#"):
                    line = line.strip("#").strip()

                columns = [str(i).strip() for i in line.split(self.delimiter)]
        else:
            # Cria nomes para as colunas de forma sequencial [0...len(headers)]
            # o Resultado é uma lista de str: ['0', ...,'10',...]
            df = pd.read_csv(
                self.filepath,
                delimiter=self.delimiter,
                skiprows=self.skiprows,
                header=None,
                delim_whitespace=self.delim_whitespace,
            )
            columns = [str(i) for i in [*range(0, len(df.iloc[0]))]]
        return columns

    def get_delimiter(self):
        """Get delimiter from file

        Returns:
            str: delimiter
        """
        with open(self.filepath, "r") as csvfile:
            dt = csvfile.readline().replace("\n", "")
            delimiter = csv.Sniffer().sniff(dt).delimiter

        if delimiter.isspace():
            return None

        return delimiter

    def count_skiprows(
        self,
    ):
        count = 0
        with open(self.filepath, "r") as f:
            for line in f:
                if line.startswith("#") or self.is_line_str(line.strip("\r\n")):
                    count += 1
                else:
                    break
        return count

    def is_line_str(self, line):
        return all(
            (
                isinstance(el, str) and not el.isnumeric()
                for el in line.split(self.delimiter)
            )
        )
