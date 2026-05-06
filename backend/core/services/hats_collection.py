import logging
import os
import pathlib
import shutil
import stat
import tarfile
import tempfile
import zipfile

from django.conf import settings

LOGGER = logging.getLogger("django")

HATS_ARCHIVE_EXTENSIONS = (".tar", ".tar.gz", ".tgz", ".zip")
HATS_REJECTED_PRODUCT_TYPES = {"training_results"}
DEFAULT_MAX_MEMBERS = 200000
DEFAULT_MAX_EXTRACTED_SIZE = 20 * 1024 * 1024 * 1024


class HatsArchiveError(ValueError):
    pass


class NotHatsCollectionError(HatsArchiveError):
    pass


class UnsafeArchiveError(HatsArchiveError):
    pass


def is_hats_archive_name(filename):
    name = filename.lower()
    return name.endswith(HATS_ARCHIVE_EXTENSIONS)


def product_type_accepts_hats(product_type_name):
    return product_type_name not in HATS_REJECTED_PRODUCT_TYPES


def _is_relative_safe_path(path):
    candidate = pathlib.PurePosixPath(path.replace("\\", "/"))
    return not candidate.is_absolute() and ".." not in candidate.parts


def _safe_target(root, member_name):
    target = pathlib.Path(root, member_name).resolve()
    root = pathlib.Path(root).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise UnsafeArchiveError(f"Unsafe archive path: {member_name}") from exc
    return target


def _check_member_count(count):
    max_members = getattr(settings, "HATS_MAX_ARCHIVE_MEMBERS", DEFAULT_MAX_MEMBERS)
    if count > max_members:
        raise UnsafeArchiveError(
            f"Archive has too many members ({count}; maximum is {max_members})."
        )


def _check_total_size(total_size):
    max_size = getattr(
        settings, "HATS_MAX_EXTRACTED_SIZE", DEFAULT_MAX_EXTRACTED_SIZE
    )
    if total_size > max_size:
        raise UnsafeArchiveError(
            "Archive extracted size exceeds the configured limit "
            f"({total_size} bytes; maximum is {max_size})."
        )


def _extract_tar(archive_path, destination):
    total_size = 0
    with tarfile.open(archive_path) as tar:
        members = tar.getmembers()
        _check_member_count(len(members))

        for member in members:
            if not _is_relative_safe_path(member.name):
                raise UnsafeArchiveError(f"Unsafe archive path: {member.name}")
            if member.issym() or member.islnk() or member.isdev():
                raise UnsafeArchiveError(
                    f"Archive member is not a regular file or directory: {member.name}"
                )
            if member.isfile():
                total_size += member.size
                _check_total_size(total_size)

        for member in members:
            target = _safe_target(destination, member.name)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            if member.isfile():
                target.parent.mkdir(parents=True, exist_ok=True)
                source = tar.extractfile(member)
                if source is None:
                    raise UnsafeArchiveError(
                        f"Could not read archive member: {member.name}"
                    )
                with source, open(target, "wb") as output:
                    shutil.copyfileobj(source, output)


def _zip_member_is_symlink(info):
    mode = info.external_attr >> 16
    return stat.S_ISLNK(mode)


def _extract_zip(archive_path, destination):
    total_size = 0
    with zipfile.ZipFile(archive_path) as zip_archive:
        members = zip_archive.infolist()
        _check_member_count(len(members))

        for member in members:
            if not _is_relative_safe_path(member.filename):
                raise UnsafeArchiveError(f"Unsafe archive path: {member.filename}")
            if _zip_member_is_symlink(member):
                raise UnsafeArchiveError(
                    f"Archive member is not a regular file or directory: {member.filename}"
                )
            if not member.is_dir():
                total_size += member.file_size
                _check_total_size(total_size)

        for member in members:
            target = _safe_target(destination, member.filename)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with zip_archive.open(member) as source, open(target, "wb") as output:
                shutil.copyfileobj(source, output)


def _extract_archive(archive_path, destination):
    name = archive_path.name.lower()
    if name.endswith((".tar", ".tar.gz", ".tgz")):
        _extract_tar(archive_path, destination)
        return

    if name.endswith(".zip"):
        _extract_zip(archive_path, destination)
        return

    raise NotHatsCollectionError("Unsupported HATS archive extension.")


def _candidate_roots(extracted_dir):
    roots = []
    for root, dirs, files in os.walk(extracted_dir):
        file_names = set(files)
        if "collection.properties" in file_names or "hats.properties" in file_names:
            roots.append(pathlib.Path(root))
    return roots


def _read_properties_file(path):
    data = {}
    if not path.exists():
        return data

    with open(path, encoding="utf-8") as properties:
        for raw_line in properties:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip().replace("\\:", ":")
    return data


def _to_jsonable_dtypes(dtypes):
    return {str(column): str(dtype) for column, dtype in dtypes.items()}


def _validate_with_lsdb(candidate):
    try:
        import lsdb
    except ImportError as exc:
        raise HatsArchiveError(
            "LSDB is not installed in the backend environment; "
            "HATS validation cannot be performed."
        ) from exc

    try:
        catalog = lsdb.open_catalog(candidate)
    except Exception as exc:
        raise NotHatsCollectionError(f"Archive is not a valid HATS collection: {exc}")

    columns = [str(column) for column in getattr(catalog, "all_columns", [])]
    if not columns:
        columns = [str(column) for column in getattr(catalog, "columns", [])]

    metadata = {
        "columns": columns,
        "dtypes": _to_jsonable_dtypes(getattr(catalog, "dtypes", {})),
        "npartitions": getattr(catalog, "npartitions", None),
        "name": getattr(catalog, "name", None),
        "hats": _read_properties_file(pathlib.Path(candidate, "hats.properties")),
        "collection": _read_properties_file(
            pathlib.Path(candidate, "collection.properties")
        ),
    }

    n_rows = metadata["hats"].get("hats_nrows")
    if n_rows is not None:
        try:
            metadata["n_rows"] = int(n_rows)
        except ValueError:
            metadata["n_rows"] = None

    return metadata


def _find_hats_root(extracted_dir):
    validation_errors = []
    for candidate in _candidate_roots(extracted_dir):
        try:
            metadata = _validate_with_lsdb(candidate)
            return candidate, metadata
        except NotHatsCollectionError as exc:
            validation_errors.append(str(exc))

    message = "Archive does not contain a valid HATS collection."
    if validation_errors:
        message = f"{message} {'; '.join(validation_errors)}"
    raise NotHatsCollectionError(message)


def _write_upload_to_temp(uploaded_file, tmpdir):
    suffix = pathlib.Path(uploaded_file.name).suffix
    name = uploaded_file.name.lower()
    if name.endswith(".tar.gz"):
        suffix = ".tar.gz"
    elif name.endswith(".tgz"):
        suffix = ".tgz"

    archive_path = pathlib.Path(tmpdir, f"upload{suffix}")
    with open(archive_path, "wb") as output:
        for chunk in uploaded_file.chunks():
            output.write(chunk)
    return archive_path


def validate_and_store_hats_archive(uploaded_file, product, target_name="main"):
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = _write_upload_to_temp(uploaded_file, tmpdir)
        extracted_dir = pathlib.Path(tmpdir, "extracted")
        extracted_dir.mkdir()

        _extract_archive(archive_path, extracted_dir)
        hats_root, metadata = _find_hats_root(extracted_dir)

        product_root = pathlib.Path(settings.MEDIA_ROOT, product.path)
        target = pathlib.Path(product_root, target_name)
        if target.exists():
            raise HatsArchiveError(
                f"A HATS collection already exists for this product at '{target_name}'."
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(hats_root), str(target))

    relative_path = pathlib.Path(product.path, target_name)
    return str(relative_path), metadata


def validate_hats_archive(uploaded_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        archive_path = _write_upload_to_temp(uploaded_file, tmpdir)
        extracted_dir = pathlib.Path(tmpdir, "extracted")
        extracted_dir.mkdir()

        _extract_archive(archive_path, extracted_dir)
        _, metadata = _find_hats_root(extracted_dir)
        return metadata
