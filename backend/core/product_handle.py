import abc
from pathlib import Path
from typing import List

import pandas as pd
import tables_io

from core._typing import Column, PathLike


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

    _handle = None

    def __init__(self, filepath: PathLike):

        fp = Path(filepath)

        # Identificar o formato do arquivo
        extension = fp.suffix

        # Instancia o Handle de acordo com o tipo de arquivo
        match extension:
            case ".csv":
                self._handle = CsvHandle(fp)
            case ".fits":
                self._handle = TableIOHandle(fp)
            case ".fit":
                self._handle = TableIOHandle(fp)
            case ".hf5":
                self._handle = TableIOHandle(fp)
            case ".hdf5":
                self._handle = TableIOHandle(fp)
            case ".h5":
                self._handle = TableIOHandle(fp)
            case ".pq":
                self._handle = TableIOHandle(fp)
            # TODO: .zip, .tar, .tar.gz
            case _:
                message = f"The {extension} extension has not yet been implemented"
                raise Exception(message)

    def to_df(self, **kwargs):
        return self._handle.to_df(**kwargs)


class BaseHandle(object):
    filepath = None

    def __init__(self, filepath: PathLike):
        self.filepath = filepath

    @abc.abstractmethod
    def to_df(self, **kwargs) -> pd.DataFrame:
        pass


class CsvHandle(BaseHandle):

    has_hd = bool  # True se o arquivo CSV possuir Headers na primeira linha.
    column_names = [Column]  # Lista com nome das colunas que podem ser str ou int.

    def __init__(self, filepath: PathLike):

        super().__init__(filepath)

        self.has_hd = self.has_header()
        self.column_names = self.get_column_names()

    def to_df(self, **kwargs) -> pd.DataFrame:

        # Check for header parameter
        if "header" in kwargs:
            raise Exception(
                "It is not possible to use the header argument in the df_from_file() method when the file is a .csv file."
            )

        if self.has_hd:
            df = pd.read_csv(self.filepath, header=0, **kwargs)
        else:
            df = pd.read_csv(
                self.filepath, header=None, names=self.column_names, **kwargs
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
        df = pd.read_csv(self.filepath, header=None, nrows=20)
        df_header = pd.read_csv(self.filepath, nrows=20)
        if tuple(df.dtypes) != tuple(df_header.dtypes):
            temp.append(True)
        else:
            temp.append(False)

        # Method: Check if at least one in first Line is String.
        # https://stackoverflow.com/questions/38360496/pandas-read-csv-without-knowing-whether-header-is-present/62217716#62217716
        df = pd.read_csv(self.filepath, header=None, nrows=20)
        if any(df.iloc[0].apply(lambda x: isinstance(x, str))):
            temp.append(True)
        else:
            temp.append(False)
        return all(temp)

    def get_column_names(self) -> List[Column]:

        if self.has_hd:
            df = pd.read_csv(self.filepath, header=None, nrows=5)
            df = df[1:].reset_index(drop=True).rename(columns=df.iloc[0])
            columns = df.columns.tolist()
        else:
            # Cria nomes para as colunas de forma sequencial [0...len(headers)]
            # o Resultado é uma lista de str: ['0', ...,'10',...]
            df = pd.read_csv(self.filepath, header=None, nrows=5)
            columns = [str(i) for i in [*range(0, len(df.iloc[0]))]]

        return columns


class TableIOHandle(BaseHandle):
    def __init__(self, filepath: PathLike):

        super().__init__(filepath)

    def to_df(self, **kwargs) -> pd.DataFrame:
        # TODO: Tratar arquivos com mais de uma tabela.

        # Le o arquivo utilizando o metodo read da tables_io
        # O retorno é um astropy table.
        tb_ap = tables_io.read(self.filepath)
        # Converte o astropy table para pandas.Dataframe
        df = tables_io.convert(tb_ap, tables_io.types.PD_DATAFRAME)

        return df
