import pathlib
import logging

from django.conf import settings

LOGGER = logging.getLogger("django")


class InputsBuilder:

    COLUMN_MAP = {
        "ra": "RA",
        "dec": "Dec",
        "z": "z",
        "id": "id",
        "z_flag": "z_flag",
        "z_err": "z_err",
        "survey": "survey",
    }

    REQUIRED_COLUMNS = {"ra", "dec", "z"}

    def __init__(self, process):
        self.process = process

    def build(self):
        inputfiles = []

        for product in self.process.inputs.all():
            main_file = product.files.get(role=0)

            filepath = pathlib.Path(
                settings.UPLOAD_DIR,
                product.path,
                main_file.name,
            )

            if not filepath.is_file():
                raise FileNotFoundError(f"file not found: {filepath}")

            inputfiles.append({
                "path": str(filepath),
                "format": main_file.extension.replace(".", ""),
                "columns": self._build_columns(product),
                "internal_name": product.internal_name,
            })

        return inputfiles

    def _build_columns(self, product):
        columns = {}

        for output_name, alias in self.COLUMN_MAP.items():
            column = self._get_column(product, alias)

            if column is None and output_name in self.REQUIRED_COLUMNS:
                raise ValueError(
                    f"Required column '{alias}' not mapped for product {product}"
                )

            columns[output_name] = column

        return columns

    def _get_column(self, product, alias):
        matches = product.contents.filter(alias=alias)

        if matches.count() != 1:
            LOGGER.warning(
                f"Column {alias} not mapped for product {product}"
            )

            if alias.lower() in ("ra", "dec", "z"):
                return alias.lower()

            return None

        return matches.first().column_name