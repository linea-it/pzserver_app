import shutil
from pathlib import Path

from core.models import (
    FileRoles,
    Product,
    ProductContent,
    ProductFile,
    ProductStatus,
    ProductType,
    Release,
)
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


PRODUCT_INTERNAL_NAME = "local_dp1_specz_collection"
PRODUCT_PATH = f"redshift_catalog/{PRODUCT_INTERNAL_NAME}"
COLLECTION_NAME = "dp1_specz_collection"

COLUMNS = (
    ("CRD_ID", None),
    ("id", "ID"),
    ("ra", "RA"),
    ("dec", "Dec"),
    ("z", "z"),
    ("z_flag", "z_flag"),
    ("z_err", "z_err"),
    ("instrument_type", None),
    ("survey", "survey"),
    ("source", None),
    ("tie_result", None),
    ("is_in_rubin_footprint", None),
    ("compared_to", None),
    ("z_flag_homogenized", None),
    ("instrument_type_homogenized", None),
    ("group_id", None),
    ("_healpix_29", None),
)


class Command(BaseCommand):
    help = "Register the local DP1 HATS spectroscopic collection as a product"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            help="Owner username; defaults to the first active superuser.",
        )

    def handle(self, *args, **options):
        source = Path(settings.DATASETS_DIR, COLLECTION_NAME)
        properties = source / "collection.properties"
        if not properties.is_file():
            raise CommandError(f"DP1 spectroscopic collection not found: {source}")

        user = self._get_user(options.get("username"))
        release = Release.objects.get(name="dp1")
        product_type = ProductType.objects.get(name="redshift_catalog")

        destination = Path(settings.UPLOAD_DIR, PRODUCT_PATH, COLLECTION_NAME)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, dirs_exist_ok=True)

        row_count = self._read_row_count(source, properties)
        size = sum(path.stat().st_size for path in destination.rglob("*") if path.is_file())

        with transaction.atomic():
            product, created = Product.objects.update_or_create(
                internal_name=PRODUCT_INTERNAL_NAME,
                defaults={
                    "product_type": product_type,
                    "release": release,
                    "user": user,
                    "display_name": "DP1 Spectroscopic Sample",
                    "official_product": True,
                    "description": "Local HATS spectroscopic sample for DP1 end-to-end runs",
                    "status": ProductStatus.PUBLISHED,
                    "path": PRODUCT_PATH,
                },
            )
            ProductFile.objects.update_or_create(
                product=product,
                role=FileRoles.MAIN,
                defaults={
                    "file": f"{PRODUCT_PATH}/{COLLECTION_NAME}",
                    "name": COLLECTION_NAME,
                    "type": "application/x-hats",
                    "n_rows": row_count,
                    "size": size,
                    "extension": "",
                    "is_directory": True,
                },
            )
            product.contents.all().delete()
            ProductContent.objects.bulk_create(
                [
                    ProductContent(
                        product=product,
                        column_name=column_name,
                        alias=alias,
                        order=order,
                    )
                    for order, (column_name, alias) in enumerate(COLUMNS)
                ]
            )

        action = "Created" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"{action} product {product.pk}: {product.display_name} "
                f"({row_count} rows)"
            )
        )

    def _get_user(self, username):
        users = get_user_model().objects.filter(is_active=True)
        if username:
            try:
                return users.get(username=username)
            except get_user_model().DoesNotExist as exc:
                raise CommandError(f"Active user not found: {username}") from exc

        user = users.filter(is_superuser=True).order_by("pk").first()
        if user is None:
            raise CommandError(
                "No active superuser found; provide an owner with --username."
            )
        return user

    @staticmethod
    def _read_row_count(collection_path, properties_path):
        collection_properties = Command._read_properties(properties_path)
        primary_table = collection_properties.get("hats_primary_table_url")
        if not primary_table:
            raise CommandError(
                f"hats_primary_table_url not found in {properties_path}"
            )

        catalog_path = collection_path / primary_table
        for filename in ("properties", "hats.properties"):
            catalog_properties_path = catalog_path / filename
            if not catalog_properties_path.is_file():
                continue
            catalog_properties = Command._read_properties(catalog_properties_path)
            if "hats_nrows" in catalog_properties:
                return int(catalog_properties["hats_nrows"])

        raise CommandError(f"hats_nrows not found under {catalog_path}")

    @staticmethod
    def _read_properties(path):
        properties = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            properties[key.strip()] = value.strip()
        return properties
