import hashlib
import json
import pathlib
import secrets
import time
import zipfile
from urllib.parse import urlencode

import yaml
from core.models import ProductDownloadArchiveStatus, ProductStatus
from django.conf import settings
from django.core import signing
from django.utils import timezone


class ProductDownloadArchiveService:
    metadata_filename = "product_metadata.yaml"
    download_token_salt = "product-download-archive"

    @classmethod
    def prepare_archive(cls, archive):
        product = archive.product
        product_path = pathlib.Path(settings.MEDIA_ROOT, product.path)
        output_dir = cls.get_archive_output_dir(product)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_signature = cls.build_source_signature(product_path)
        metadata = cls.build_product_metadata(product)
        zip_path = cls.build_zip(
            product.internal_name,
            product_path,
            metadata,
            output_dir,
        )
        archive_path = cls.get_archive_relative_path(zip_path)
        now = timezone.now()

        archive.status = ProductDownloadArchiveStatus.READY
        archive.archive_path = archive_path
        archive.filename = zip_path.name
        archive.size = zip_path.stat().st_size
        archive.checksum = cls.build_file_checksum(zip_path)
        archive.source_signature = source_signature
        archive.source_updated_at = now
        archive.error_message = None
        archive.save(
            update_fields=[
                "status",
                "archive_path",
                "filename",
                "size",
                "checksum",
                "source_signature",
                "source_updated_at",
                "error_message",
                "updated_at",
            ]
        )

        return archive

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
    def build_product_metadata(cls, product):
        metadata = {
            "id": product.pk,
            "release": product.release.pk if product.release else None,
            "release_name": product.release.display_name if product.release else None,
            "release_year": product.release_year,
            "product_type": product.product_type.pk,
            "product_type_name": product.product_type.display_name,
            "product_type_internal_name": product.product_type.name,
            "uploaded_by": product.user.username,
            "origin": (
                product.process.pipeline.display_name
                if hasattr(product, "process")
                else "Upload"
            ),
            "process_status": (
                product.process.status if hasattr(product, "process") else None
            ),
            "process_id": product.process.pk if hasattr(product, "process") else None,
            "product_status": ProductStatus(product.status).label,
            "internal_name": product.internal_name,
            "display_name": product.display_name,
            "official_product": product.official_product,
            "pz_code": product.pz_code,
            "description": product.description,
            "created_at": product.created_at.isoformat(),
            "status": product.status,
            "updated_at": product.updated_at.isoformat(),
        }

        for product_file in product.files.all().order_by("role", "name"):
            file_data = {
                "name": product_file.name,
                "type": product_file.type,
                "extension": product_file.extension,
                "size": product_file.size,
                "n_rows": product_file.n_rows,
            }

            if product_file.role == 0:
                metadata["main_file"] = file_data
                product_contents = cls.build_product_contents_metadata(product)
                if product_contents:
                    metadata["associated_columns"] = product_contents
            else:
                metadata.setdefault("attach_files", []).append(
                    {"name": product_file.name, "type": product_file.type}
                )

        return metadata

    @classmethod
    def build_product_contents_metadata(cls, product):
        contents = []

        for content in product.contents.all():
            if not content.alias:
                continue

            contents.append(
                {
                    "column_name": content.column_name,
                    "ucd": content.ucd,
                    "alias": content.alias,
                }
            )

        return contents

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
    def build_file_checksum(cls, file_path):
        digest = hashlib.sha256()

        with open(file_path, "rb") as file_handle:
            for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
                digest.update(chunk)

        return digest.hexdigest()

    @classmethod
    def find_current_archive(cls, product, source_signature):
        ready_archive = cls.find_ready_archive(product, source_signature)
        if ready_archive:
            return ready_archive

        return (
            product.download_archives.filter(source_signature=source_signature)
            .filter(
                status__in=[
                    ProductDownloadArchiveStatus.PENDING,
                    ProductDownloadArchiveStatus.RUNNING,
                    ProductDownloadArchiveStatus.FAILED,
                ]
            )
            .order_by("-created_at")
            .first()
        )

    @classmethod
    def find_ready_archive(cls, product, source_signature):
        archives = (
            product.download_archives.filter(
                source_signature=source_signature,
                status=ProductDownloadArchiveStatus.READY,
                archive_path__isnull=False,
            )
            .exclude(archive_path="")
            .order_by("-created_at")
        )

        for archive in archives:
            if cls.archive_file_exists(archive):
                return archive

        return None

    @classmethod
    def archive_file_exists(cls, archive):
        return cls.get_archive_file_path(archive).is_file()

    @classmethod
    def get_archive_file_path(cls, archive):
        archive_path = pathlib.Path(archive.archive_path)

        if archive_path.is_absolute():
            return archive_path

        return pathlib.Path(settings.MEDIA_ROOT, archive_path)

    @classmethod
    def build_download_url(cls, archive, user, request=None):
        token = cls.build_download_token(archive, user)
        path = (
            f"/api/products/{archive.product_id}/download/file/"
            f"?{urlencode({'token': token})}"
        )

        if request:
            return request.build_absolute_uri(path)

        return path

    @classmethod
    def build_download_token(cls, archive, user):
        return signing.dumps(
            {
                "archive_id": archive.pk,
                "product_id": archive.product_id,
                "user_id": user.pk,
            },
            salt=cls.download_token_salt,
        )

    @classmethod
    def load_download_token(cls, token):
        return signing.loads(
            token,
            salt=cls.download_token_salt,
            max_age=cls.get_download_token_max_age_seconds(),
        )

    @classmethod
    def get_download_token_max_age_seconds(cls):
        return getattr(settings, "PRODUCT_DOWNLOAD_TOKEN_MAX_AGE_SECONDS", 900)

    @classmethod
    def wait_for_archive_preparation(cls, archive):
        wait_seconds = cls.get_prepare_wait_seconds()
        if wait_seconds <= 0:
            return archive

        deadline = time.monotonic() + wait_seconds

        while time.monotonic() < deadline:
            archive.refresh_from_db()
            if archive.status not in (
                ProductDownloadArchiveStatus.PENDING,
                ProductDownloadArchiveStatus.RUNNING,
            ):
                return archive

            time.sleep(cls.get_prepare_poll_interval_seconds())

        archive.refresh_from_db()
        return archive

    @classmethod
    def get_prepare_wait_seconds(cls):
        return getattr(settings, "PRODUCT_DOWNLOAD_PREPARE_WAIT_SECONDS", 10)

    @classmethod
    def get_prepare_poll_interval_seconds(cls):
        return getattr(
            settings,
            "PRODUCT_DOWNLOAD_PREPARE_POLL_INTERVAL_SECONDS",
            0.5,
        )

    @classmethod
    def get_archive_output_dir(cls, product):
        return cls.get_archive_root() / "products" / str(product.pk)

    @classmethod
    def get_archive_root(cls):
        return pathlib.Path(settings.PRODUCT_DOWNLOAD_ROOT)

    @classmethod
    def get_archive_relative_path(cls, archive_path):
        archive_path = pathlib.Path(archive_path)

        try:
            return archive_path.relative_to(settings.MEDIA_ROOT).as_posix()
        except ValueError:
            return archive_path.as_posix()

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
