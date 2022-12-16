import tarfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import tables_io
from astropy.table import Table


def sample_product_file(extension="csv", compression=None, header=True):
    data = [
        {
            "coadd_objects_id": 18599476134425520,
            "z_true": 2.8423803,
            "ra": 60.4467,
            "dec": -34.056,
            "extendedness": 1,
            "mag_g": 25.7714,
        },
        {
            "coadd_objects_id": 18617081205359130,
            "z_true": 1.2903498,
            "ra": 67.6464,
            "dec": -33.5759,
            "extendedness": 1,
            "mag_g": 27.2174,
        },
        {
            "coadd_objects_id": 14373666401847352,
            "z_true": 1.4635979,
            "ra": 73.0255,
            "dec": -40.2059,
            "extendedness": 1,
            "mag_g": 23.5788,
        },
        {
            "coadd_objects_id": 22293706354760120,
            "z_true": 0.13579375,
            "ra": 63.8322,
            "dec": -27.6616,
            "extendedness": 1,
            "mag_g": 24.5015,
        },
        {
            "coadd_objects_id": 22302919059604932,
            "z_true": 0.7892432,
            "ra": 66.3111,
            "dec": -27.5326,
            "extendedness": 0,
            "mag_g": 27.6267,
        },
        {
            "coadd_objects_id": 20412167081697070,
            "z_true": 0.4667132,
            "ra": 58.9066,
            "dec": -30.6574,
            "extendedness": 1,
            "mag_g": 27.6149,
        },
        {
            "coadd_objects_id": 12776333704719100,
            "z_true": 1.5876242,
            "ra": 68.1112,
            "dec": -44.1935,
            "extendedness": 1,
            "mag_g": 27.9899,
        },
        {
            "coadd_objects_id": 16844681346314150,
            "z_true": 1.4169712,
            "ra": 60.7199,
            "dec": -35.866,
            "extendedness": 0,
            "mag_g": 27.2421,
        },
        {
            "coadd_objects_id": 17733619317508160,
            "z_true": 0.73940337,
            "ra": 67.4605,
            "dec": -35.192,
            "extendedness": 1,
            "mag_g": 29.4996,
        },
    ]

    df = pd.DataFrame(
        data=data,
        columns=[
            "coadd_objects_id",
            "z_true",
            "ra",
            "dec",
            "extendedness",
            "mag_g",
        ],
    )
    filename = f"sample_file.{extension}"
    filepath = Path("/tmp/", filename)
    result = filepath

    if extension == "csv":
        df.to_csv(filepath, index=False, header=header)

    elif extension in ["fits", "hf5", "hdf5", "h5", "pq"]:
        # Cria uma Astropy Table
        td_ap = Table(data)

        result = Path("/tmp/", "sample_file")
        tempResult = Path("/tmp/", f"sample_file.{extension}")
        if tempResult.exists():
            tempResult.unlink()
        tables_io.write(td_ap, str(result), extension)
        result = tempResult

    if compression == "zip":
        filename = "sample_file.zip"
        result = Path("/tmp/", filename)
        with zipfile.ZipFile(result, mode="w") as archive:
            archive.write(filepath)

    elif compression in ["tar", "gz"]:
        filename = "sample_file.tar.gz" if compression == "gz" else "sample_file.tar"
        result = Path("/tmp/", filename)
        with tarfile.open(result, "w:gz") as tar:
            tar.add(filepath)

    return result
