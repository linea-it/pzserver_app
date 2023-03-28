import json

import pandas as pd
import pytest
from core.product_handle import BaseHandle, CsvHandle, NotTableError, ProductHandle
from core.test.util import sample_product_file
from rest_framework.test import APIRequestFactory, APITestCase


class TestProductHandleClass(APITestCase):
    def setUp(self):
        self.countRows = 9
        self.columns = [
            "coadd_objects_id",
            "z_true",
            "ra",
            "dec",
            "extendedness",
            "mag_g",
        ]
        self.numbered_columns = ["0", "1", "2", "3", "4", "5"]

        self.tcases = [
            {"extension": "csv", "header": True, "compression": None},
            {"extension": "csv", "header": False, "compression": None},
            {"extension": "csv", "header": True, "compression": "zip"},
            {"extension": "csv", "header": False, "compression": "zip"},
            {"extension": "csv", "header": True, "compression": "tar"},
            {"extension": "csv", "header": False, "compression": "tar"},
            {"extension": "csv", "header": True, "compression": "gz"},
            {"extension": "csv", "header": False, "compression": "gz"},
            {"extension": "fits", "header": True, "compression": None},
            {"extension": "fits", "header": True, "compression": "tar"},
            {"extension": "fits", "header": True, "compression": "gz"},
            {"extension": "hf5", "header": True, "compression": None},
            {"extension": "hf5", "header": True, "compression": "tar"},
            {"extension": "hf5", "header": True, "compression": "gz"},
            {"extension": "hdf5", "header": True, "compression": None},
            {"extension": "hdf5", "header": True, "compression": "tar"},
            {"extension": "hdf5", "header": True, "compression": "gz"},
            {"extension": "h5", "header": True, "compression": None},
            {"extension": "h5", "header": True, "compression": "tar"},
            {"extension": "h5", "header": True, "compression": "gz"},
            {"extension": "pq", "header": True, "compression": None},
            {"extension": "pq", "header": True, "compression": "tar"},
            {"extension": "pq", "header": True, "compression": "gz"},
            {
                "extension": "txt",
                "header": False,
                "compression": None,
                "delimiter": " ",
            },
            {
                "extension": "txt",
                "header": False,
                "compression": None,
                "delimiter": "  ",
            },
            {
                "extension": "txt",
                "header": False,
                "compression": None,
                "delimiter": ";",
            },
            {
                "extension": "txt",
                "header": True,
                "compression": None,
                "delimiter": " ",
            },
            {
                "extension": "txt",
                "header": True,
                "compression": None,
                "delimiter": " ",
                "commented_lines": 1,
            },
            {
                "extension": "txt",
                "header": False,
                "compression": None,
                "delimiter": " ",
                "commented_lines": 5,
            },
            {
                "extension": "txt",
                "header": False,
                "compression": None,
                "delimiter": " ",
                "str_value": True,
            },
        ]

    def test_df_from_file(self):
        for tcase in self.tcases:
            # Cria o arquivo de teste
            sample_file = sample_product_file(**tcase)

            if tcase["compression"] != None:
                with pytest.raises(NotTableError):
                    ProductHandle().df_from_file(sample_file)

            else:
                df = ProductHandle().df_from_file(sample_file)
                # Verifica se o resultado é um Dataframe para
                self.assertEqual(type(df), pd.DataFrame)

                # Quantidade de Registros
                self.assertEqual(df.shape[0], self.countRows)

                # Verifica as colunas do dataframe
                if tcase["header"]:
                    self.assertEqual(sorted(df.columns.to_list()), sorted(self.columns))
                else:
                    self.assertEqual(df.columns.to_list(), self.numbered_columns)

    def test_csv_handle_param_exception(self):
        sample_file = sample_product_file(
            extension="csv",
            header=True,
            compression=None,
        )

        with pytest.raises(Exception):
            CsvHandle(sample_file).to_df(header=True)

        with pytest.raises(Exception):
            CsvHandle(sample_file).to_df(delimiter=",")

    # def test_extension_not_implemented_exception(self):
    #     sample_file = sample_product_file(
    #         extension="csv",
    #         header=True,
    #         compression=None,
    #     )
    #     sample_file.rename("/tmp/sample_file.dat")
    #     with pytest.raises(NotImplementedError):
    #         ProductHandle().df_from_file("/tmp/sample_file.dat")

    def test_base_handle_to_df_exception(self):
        sample_file = sample_product_file(
            extension="csv",
            header=True,
            compression=None,
        )
        with pytest.raises(NotImplementedError):
            BaseHandle(sample_file).to_df()

    # def test_txt_handle_str_value_exception(self):
    #     sample_file = sample_product_file(
    #         extension="txt",
    #         header=True,
    #         compression=None,
    #         delimiter=" ",
    #         commented_lines=0,
    #         str_value=True,
    #     )
    #     with pytest.raises(ValueError):
    #         ProductHandle().df_from_file(sample_file)
