import hashlib
import json
import pathlib
import secrets
import zipfile

import yaml
from django.conf import settings


class ProductDownloadArchiveService:
    metadata_filename = "product_metadata.yaml"

    @classmethod
    def build_zip(cls, internal_name, product_path, metadata, output_dir):
        product_path = pathlib.Path(product_path)
        output_dir = pathlib.Path(output_dir)
        zip_path = output_dir / f"{internal_name}_{secrets.token_hex(16)}.zip"

        with zipfile.ZipFile(
            zip_path,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=cls.get_compression_level(),
        ) as zip_handle:
            zip_handle.writestr(cls.metadata_filename, cls._dump_metadata(metadata))

            for file_path, arcname in cls.iter_source_files(product_path):
                zip_handle.write(file_path, arcname=arcname)

        return zip_path

    @classmethod
    def build_source_snapshot(cls, product_path):
        snapshot = []

        for file_path, arcname in cls.iter_source_files(product_path):
            file_stat = file_path.stat()
            snapshot.append(
                {
                    "path": arcname,
                    "size": file_stat.st_size,
                    "mtime_ns": file_stat.st_mtime_ns,
                }
            )

        return snapshot

    @classmethod
    def build_source_signature(cls, product_path):
        snapshot = cls.build_source_snapshot(product_path)
        payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"))

        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def iter_source_files(cls, product_path):
        product_path = pathlib.Path(product_path)

        for file_path in sorted(product_path.rglob("*")):
            if not file_path.is_file():
                continue

            arcname = file_path.relative_to(product_path).as_posix()
            if arcname == cls.metadata_filename:
                continue

            yield file_path, arcname

    @classmethod
    def get_compression_level(cls):
        return getattr(settings, "PRODUCT_DOWNLOAD_COMPRESSION_LEVEL", 6)

    @classmethod
    def _dump_metadata(cls, metadata):
        return yaml.dump(
            metadata,
            default_flow_style=False,
            allow_unicode=False,
            encoding=None,
        )
