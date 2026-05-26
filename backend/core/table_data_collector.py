import logging
import pathlib
import shutil
import tarfile
import tempfile
import zipfile
from gzip import open as gzip_open

import pandas as pd
import pyarrow.parquet as pq
from core.file_utils import get_file_extension
from core.product_handle import CsvHandle, FileHandle, NotTableError, ProductHandle, TxtHandle

LOGGER = logging.getLogger("products")


class MainTableDataCollector:
    """Collects tabular metadata and preview rows from a product main file."""

    def __init__(self, main_file, preview_rows, tabular_suffixes):
        """Initialize a collector for a given main file.

        Args:
            main_file (pathlib.Path): Path to the product main file.
            preview_rows (int): Maximum number of preview rows to collect.
            tabular_suffixes (set[str]): Supported tabular file extensions.
        """
        self.main_file = pathlib.Path(main_file)
        self.preview_rows = preview_rows
        self.tabular_suffixes = tabular_suffixes
        self._compressed_members_cache = None

    def collect(self):
        """Collect preview rows, column names, and total row count.

        Returns:
            dict: A dictionary with keys `preview_df`, `columns`, and `n_rows`.

        Raises:
            NotTableError: If no tabular content can be extracted from the file.
        """
        if self.main_file.is_dir():
            return self._collect_from_hats_directory(self.main_file)

        if self._is_compressed_main_file():
            return self._collect_from_compressed_main_file()
        return self._collect_from_path(self.main_file)

    def is_compressed_main_file(self):
        """Public helper to check whether the main file is compressed."""
        return self._is_compressed_main_file()

    def inspect_compressed_main_file(self, members=None):
        """Inspect compressed main file contents and classify supported structures.

        Returns:
            dict: Information about compressed members and classification:
                - file_count (int)
                - tabular_files (list[str])
                - tabular_file_count (int)
                - is_hats (bool)
        """
        if not self._is_compressed_main_file():
            raise NotTableError("Main file is not compressed.")

        members = members if members is not None else self._list_compressed_members()
        tabular_files = [
            str(member)
            for member in members
            if get_file_extension(member.name) in self.tabular_suffixes
        ]

        return {
            "file_count": len(members),
            "tabular_files": tabular_files,
            "tabular_file_count": len(tabular_files),
            "is_hats": self._is_hats_layout(members),
        }

    def extract_supported_main_content(self, destination_dir):
        """Extract compressed content into destination directory when supported.

        Supported extraction targets:
        - Single tabular file inside the archive.
        - HATS collection layout.

        Args:
            destination_dir (str | pathlib.Path): Product directory where extracted
                content should be written.

        Returns:
            dict: Extraction details with keys:
                - kind: "tabular" or "hats"
                - path: pathlib.Path to extracted main file/directory
                - file_count: number of files in compressed source
                - tabular_file_count: number of detected tabular files
                - is_hats: bool

        Raises:
            NotTableError: If compressed content does not match supported layouts.
        """
        if not self._is_compressed_main_file():
            raise NotTableError("Main file is not compressed.")

        members = self._list_compressed_members()
        info = self.inspect_compressed_main_file(members=members)
        destination_dir = pathlib.Path(destination_dir)
        destination_dir.mkdir(parents=True, exist_ok=True)

        if info["file_count"] == 1 and info["tabular_file_count"] == 1:
            member_name = pathlib.PurePosixPath(info["tabular_files"][0])
            extracted_path = self._extract_single_member(destination_dir, member_name)
            return {
                "kind": "tabular",
                "path": extracted_path,
                "file_count": info["file_count"],
                "tabular_file_count": info["tabular_file_count"],
                "is_hats": False,
                "extracted_members": [extracted_path],
                "size_bytes": extracted_path.stat().st_size,
            }

        staging_dir = pathlib.Path(
            tempfile.mkdtemp(prefix=".__hats_extract_", dir=destination_dir)
        )
        try:
            extracted_members = self._extract_all_members(staging_dir)
            size_bytes = sum(
                path.stat().st_size for path in extracted_members if path.exists()
            )
            hats_root = self._resolve_hats_root_from_members(staging_dir, members)
            lsdb_hats = self._is_hats_with_lsdb(hats_root)

            if lsdb_hats is False:
                raise NotTableError(
                    "Compressed main file does not map to a readable HATS collection."
                )

            if lsdb_hats is None and not info["is_hats"]:
                raise NotTableError(
                    "Compressed main file does not map to a single tabular file or a HATS collection."
                )

            final_hats_root = self._finalize_hats_extraction(
                staging_dir=staging_dir,
                hats_root=hats_root,
                destination_dir=destination_dir,
            )
            return {
                "kind": "hats",
                "path": final_hats_root,
                "file_count": info["file_count"],
                "tabular_file_count": info["tabular_file_count"],
                "is_hats": True,
                "extracted_members": [final_hats_root],
                "size_bytes": size_bytes,
            }
        finally:
            if staging_dir.exists():
                shutil.rmtree(staging_dir, ignore_errors=True)

    def _is_compressed_main_file(self):
        """Identify whether the main file should be handled as compressed."""
        if self.main_file.is_dir():
            return False

        extension = get_file_extension(self.main_file.name)
        if extension in {".gz", ".gzip"}:
            return True

        return zipfile.is_zipfile(self.main_file) or tarfile.is_tarfile(self.main_file)

    def _list_compressed_members(self):
        """List non-directory member paths in compressed file."""
        if self._compressed_members_cache is not None:
            return self._compressed_members_cache

        if zipfile.is_zipfile(self.main_file):
            with zipfile.ZipFile(self.main_file) as archive:
                members = [
                    pathlib.PurePosixPath(info.filename)
                    for info in archive.infolist()
                    if not info.is_dir()
                ]
                self._compressed_members_cache = members
                return members

        if tarfile.is_tarfile(self.main_file):
            with tarfile.open(self.main_file, mode="r:*") as archive:
                members = [
                    pathlib.PurePosixPath(member.name)
                    for member in archive.getmembers()
                    if member.isfile()
                ]
                self._compressed_members_cache = members
                return members

        if get_file_extension(self.main_file.name) in {".gz", ".gzip"}:
            inferred_member = pathlib.PurePosixPath(pathlib.Path(self.main_file.stem).name)
            members = [inferred_member]
            self._compressed_members_cache = members
            return members

        self._compressed_members_cache = []
        return self._compressed_members_cache

    def _extract_all_members(self, destination_dir):
        """Extract all non-directory members into destination directory."""
        destination_dir = pathlib.Path(destination_dir)
        extracted_paths = []

        if zipfile.is_zipfile(self.main_file):
            with zipfile.ZipFile(self.main_file) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    member_path = pathlib.PurePosixPath(info.filename)
                    output_path = self._safe_member_destination(
                        destination_dir, member_path
                    )
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info, "r") as source:
                        output_path.write_bytes(source.read())
                    extracted_paths.append(output_path)
            return extracted_paths

        if tarfile.is_tarfile(self.main_file):
            with tarfile.open(self.main_file, mode="r:*") as archive:
                for member in archive.getmembers():
                    if not member.isfile():
                        continue
                    member_path = pathlib.PurePosixPath(member.name)
                    output_path = self._safe_member_destination(
                        destination_dir, member_path
                    )
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    fileobj = archive.extractfile(member)
                    if not fileobj:
                        continue
                    output_path.write_bytes(fileobj.read())
                    extracted_paths.append(output_path)
            return extracted_paths

        if get_file_extension(self.main_file.name) in {".gz", ".gzip"}:
            inferred_member = pathlib.PurePosixPath(pathlib.Path(self.main_file.stem).name)
            output_path = self._safe_member_destination(destination_dir, inferred_member)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with gzip_open(self.main_file, "rb") as source:
                output_path.write_bytes(source.read())
            return [output_path]

        raise NotTableError("Compressed extraction is not supported for this file.")

    def _extract_single_member(self, destination_dir, member_name):
        """Extract one named member into destination directory."""
        destination_dir = pathlib.Path(destination_dir)
        member_name = pathlib.PurePosixPath(member_name)

        if zipfile.is_zipfile(self.main_file):
            with zipfile.ZipFile(self.main_file) as archive:
                for info in archive.infolist():
                    if info.is_dir():
                        continue
                    candidate = pathlib.PurePosixPath(info.filename)
                    if candidate != member_name:
                        continue
                    output_path = self._safe_member_destination(
                        destination_dir, member_name
                    )
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    with archive.open(info, "r") as source:
                        output_path.write_bytes(source.read())
                    return output_path
            raise NotTableError("Tabular member not found in zip archive.")

        if tarfile.is_tarfile(self.main_file):
            with tarfile.open(self.main_file, mode="r:*") as archive:
                for member in archive.getmembers():
                    if not member.isfile():
                        continue
                    candidate = pathlib.PurePosixPath(member.name)
                    if candidate != member_name:
                        continue
                    output_path = self._safe_member_destination(
                        destination_dir, member_name
                    )
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    fileobj = archive.extractfile(member)
                    if not fileobj:
                        continue
                    output_path.write_bytes(fileobj.read())
                    return output_path
            raise NotTableError("Tabular member not found in tar archive.")

        if get_file_extension(self.main_file.name) in {".gz", ".gzip"}:
            output_path = self._safe_member_destination(destination_dir, member_name)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with gzip_open(self.main_file, "rb") as source:
                output_path.write_bytes(source.read())
            return output_path

        raise NotTableError("Compressed extraction is not supported for this file.")

    def _resolve_hats_root_from_members(self, destination_dir, members):
        """Resolve HATS root directory after extraction using hats.properties path."""
        destination_dir = pathlib.Path(destination_dir)
        hats_member = next(
            (m for m in members if m.name in self.HATS_PROPERTIES_FILENAMES),
            None,
        )
        if hats_member is None:
            return destination_dir

        parent = pathlib.Path(*hats_member.parts[:-1]) if hats_member.parts[:-1] else pathlib.Path(".")
        hats_root = (destination_dir / parent).resolve()
        return hats_root

    def _is_hats_with_lsdb(self, hats_root):
        """Validate HATS by attempting to open it with LSDB.

        Returns:
            bool | None:
                - True when LSDB confirms catalog readability.
                - False when LSDB is available but cannot open the path.
                - None when LSDB is not available in this environment.
        """
        try:
            import lsdb  # type: ignore
        except Exception:
            LOGGER.debug("LSDB is not available; falling back to layout heuristic.")
            return None

        try:
            catalog = lsdb.open_catalog(path=str(hats_root))
            _ = getattr(catalog, "columns", None)
            return True
        except Exception as error:
            LOGGER.debug("LSDB could not open HATS path %s: %s", hats_root, error)
            return False

    def _finalize_hats_extraction(self, staging_dir, hats_root, destination_dir):
        """Move validated extracted HATS directory from staging into destination."""
        staging_dir = pathlib.Path(staging_dir).resolve()
        hats_root = pathlib.Path(hats_root).resolve()
        destination_dir = pathlib.Path(destination_dir).resolve()

        if hats_root == staging_dir:
            final_root = destination_dir / f"{self.main_file.stem}_hats"
            if final_root.exists():
                shutil.rmtree(final_root, ignore_errors=True)
            shutil.move(str(staging_dir), str(final_root))
            return final_root

        if staging_dir not in hats_root.parents:
            raise NotTableError("Invalid HATS extraction root.")

        relative = hats_root.relative_to(staging_dir)
        final_root = destination_dir / relative
        if final_root.exists():
            if final_root.is_dir():
                shutil.rmtree(final_root, ignore_errors=True)
            else:
                final_root.unlink(missing_ok=True)
        final_root.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(hats_root), str(final_root))
        return final_root

    def _safe_member_destination(self, destination_dir, member_path):
        """Build a safe destination path for an archive member."""
        destination_dir = pathlib.Path(destination_dir).resolve()
        relative_parts = [part for part in pathlib.PurePosixPath(member_path).parts if part not in ("", ".")]
        if any(part == ".." for part in relative_parts):
            raise NotTableError(f"Unsafe member path in archive: {member_path}")

        output_path = destination_dir.joinpath(*relative_parts).resolve()
        if destination_dir not in output_path.parents and output_path != destination_dir:
            raise NotTableError(f"Unsafe member path in archive: {member_path}")

        return output_path

    def _is_hats_layout(self, members):
        """Infer whether compressed members look like a HATS catalog layout."""
        if not members:
            return False

        # Remove leading '.' or wrapper directories for easier matching.
        normalized_members = [pathlib.PurePosixPath(str(m).lstrip("./")) for m in members]

        has_hats_properties = any(
            member.name in self.HATS_PROPERTIES_FILENAMES
            for member in normalized_members
        )

        has_dataset_parquet = False
        has_norder_npix_parquet = False

        for member in normalized_members:
            extension = get_file_extension(member.name)
            if extension not in {".parquet", ".pq"}:
                continue

            parts = member.parts
            if "dataset" in parts:
                has_dataset_parquet = True

            has_norder = any(part.startswith("Norder=") for part in parts)
            has_npix = any(part.startswith("Npix=") for part in parts)
            if has_norder and has_npix:
                has_norder_npix_parquet = True

        return has_hats_properties and (has_dataset_parquet or has_norder_npix_parquet)

    def _collect_from_path(self, filepath):
        """Collect tabular metadata from a regular file path.

        Args:
            filepath (str | pathlib.Path): Path to the tabular file.

        Returns:
            dict: A dictionary with `preview_df`, `columns`, and `n_rows`.
        """
        suffix = pathlib.Path(filepath).suffix.lower()
        if suffix in {".parquet", ".pq"}:
            return self._collect_from_parquet(filepath)

        fh = FileHandle(filepath)
        handle = fh.handle

        if isinstance(handle, CsvHandle):
            if handle.has_hd:
                return self._collect_with_chunk_iterator(
                    pd.read_csv(
                        filepath,
                        delimiter=handle.delimiter,
                        header=0,
                        chunksize=50000,
                    ),
                    fallback_columns=handle.column_names,
                )
            return self._collect_with_chunk_iterator(
                pd.read_csv(
                    filepath,
                    delimiter=handle.delimiter,
                    header=None,
                    names=handle.column_names,
                    chunksize=50000,
                ),
                fallback_columns=handle.column_names,
            )

        if isinstance(handle, TxtHandle):
            return self._collect_with_chunk_iterator(
                pd.read_csv(
                    filepath,
                    delimiter=handle.delimiter,
                    skiprows=handle.skiprows,
                    names=handle.column_names,
                    header=None,
                    delim_whitespace=handle.delim_whitespace,
                    chunksize=50000,
                ),
                fallback_columns=handle.column_names,
            )

        # Keep legacy behavior for non-text tabular formats.
        df_full = ProductHandle().df_from_file(filepath)
        return {
            "preview_df": df_full.head(self.preview_rows),
            "columns": list(df_full.columns),
            "n_rows": int(len(df_full)),
        }

    def _collect_from_hats_directory(self, hats_root):
        """Collect metadata from a HATS directory using LSDB."""
        hats_root = pathlib.Path(hats_root)
        if not hats_root.is_dir():
            raise NotTableError("HATS root is not a directory.")

        try:
            import lsdb  # type: ignore
        except Exception as error:
            raise NotTableError(
                "LSDB dependency is required to preview HATS collections."
            ) from error

        try:
            catalog = lsdb.open_catalog(path=str(hats_root))
        except Exception as error:
            raise NotTableError(
                f"Could not open HATS collection with LSDB: {error}"
            ) from error

        columns = self._normalize_catalog_columns(getattr(catalog, "columns", None))
        if not columns:
            columns = self._normalize_catalog_columns(
                getattr(catalog, "all_columns", None)
            )

        preview_obj = catalog.head(self.preview_rows)
        preview_df = self._coerce_lsdb_preview_to_dataframe(preview_obj, columns)
        n_rows = self._estimate_lsdb_row_count(catalog)

        return {
            "preview_df": preview_df,
            "columns": list(preview_df.columns) if not columns else columns,
            "n_rows": n_rows,
        }

    def _normalize_catalog_columns(self, value):
        """Normalize LSDB catalog column-like values to a plain list of strings."""
        if value is None:
            return []

        if isinstance(value, pd.Index):
            return [str(col) for col in value.tolist()]

        if isinstance(value, (list, tuple, set)):
            return [str(col) for col in value]

        try:
            as_list = list(value)
            return [str(col) for col in as_list]
        except Exception:
            return []

    def _coerce_lsdb_preview_to_dataframe(self, preview_obj, fallback_columns):
        """Convert LSDB head result to pandas DataFrame."""
        if preview_obj is None:
            return pd.DataFrame(columns=fallback_columns)

        if isinstance(preview_obj, pd.DataFrame):
            return preview_obj.reset_index(drop=True)

        if hasattr(preview_obj, "to_pandas"):
            try:
                df = preview_obj.to_pandas()
                if isinstance(df, pd.DataFrame):
                    return df.reset_index(drop=True)
            except Exception:
                pass

        if hasattr(preview_obj, "compute"):
            computed = preview_obj.compute()
            if isinstance(computed, pd.DataFrame):
                return computed.reset_index(drop=True)
            try:
                return pd.DataFrame(computed).reset_index(drop=True)
            except Exception:
                pass

        try:
            return pd.DataFrame(preview_obj).reset_index(drop=True)
        except Exception as error:
            raise NotTableError(
                f"Could not materialize LSDB preview rows as DataFrame: {error}"
            ) from error

    def _estimate_lsdb_row_count(self, catalog):
        """Estimate LSDB row count, preferring metadata-only methods when available."""
        try:
            # LSDB exposes lazy metadata-backed length for catalogs.
            return int(len(catalog))
        except Exception:
            return None

    def _collect_from_parquet(self, filepath):
        """Collect metadata from parquet using incremental batch reads.

        Args:
            filepath (str | pathlib.Path): Path to the parquet file.

        Returns:
            dict: A dictionary with `preview_df`, `columns`, and `n_rows`.
        """
        parquet_file = pq.ParquetFile(filepath)
        columns = list(parquet_file.schema_arrow.names)

        preview_frames = []
        n_rows = 0
        remaining = self.preview_rows

        for batch in parquet_file.iter_batches(batch_size=50000):
            batch_rows = batch.num_rows
            n_rows += batch_rows

            if remaining > 0 and batch_rows > 0:
                sample_size = min(remaining, batch_rows)
                preview_frames.append(batch.slice(0, sample_size).to_pandas())
                remaining -= sample_size

        if preview_frames:
            preview_df = pd.concat(preview_frames, ignore_index=True)
        else:
            preview_df = pd.DataFrame(columns=columns)

        return {
            "preview_df": preview_df,
            "columns": columns,
            "n_rows": n_rows,
        }

    def _collect_with_chunk_iterator(self, chunk_iterator, fallback_columns):
        """Aggregate metadata from a chunk iterator.

        Args:
            chunk_iterator (Iterator[pd.DataFrame]): Iterator yielding row chunks.
            fallback_columns (list[str]): Column names to use when there are no rows.

        Returns:
            dict: A dictionary with `preview_df`, `columns`, and `n_rows`.
        """
        chunks = []
        n_rows = 0
        remaining = self.preview_rows
        columns = None

        for chunk in chunk_iterator:
            if columns is None:
                columns = list(chunk.columns)

            current_rows = len(chunk)
            n_rows += current_rows

            if remaining > 0 and current_rows > 0:
                sample = chunk.head(remaining)
                chunks.append(sample)
                remaining -= len(sample)

        if columns is None:
            columns = list(fallback_columns)

        if chunks:
            preview_df = pd.concat(chunks, ignore_index=True)
        else:
            preview_df = pd.DataFrame(columns=columns)

        return {
            "preview_df": preview_df,
            "columns": columns,
            "n_rows": n_rows,
        }

    def _collect_from_compressed_main_file(self):
        """Extract and collect metadata from compressed main files.

        Returns:
            dict: A dictionary with `preview_df`, `columns`, and `n_rows`.

        Raises:
            NotTableError: If the compressed file type is unsupported or has no tabular member.
        """
        extension = get_file_extension(self.main_file.name)

        if zipfile.is_zipfile(self.main_file):
            extracted_path = self._extract_tabular_from_zip()
        elif tarfile.is_tarfile(self.main_file):
            extracted_path = self._extract_tabular_from_tar()
        elif extension in {".gz", ".gzip"}:
            extracted_path = self._extract_tabular_from_gzip_single()
        else:
            raise NotTableError("Compressed table preview is not supported for this file.")

        try:
            return self._collect_from_path(extracted_path)
        finally:
            extracted_path.unlink(missing_ok=True)

    def _extract_tabular_from_zip(self):
        """Extract the first supported tabular file from a ZIP archive.

        Returns:
            pathlib.Path: Path to a temporary extracted file.

        Raises:
            NotTableError: If no supported tabular file exists in the archive.
        """
        with zipfile.ZipFile(self.main_file) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                member_name = pathlib.Path(info.filename)
                if member_name.suffix.lower() not in self.tabular_suffixes:
                    continue
                with archive.open(info, "r") as source:
                    content = source.read()
                return self._write_temp_file(content, member_name.suffix.lower())

        raise NotTableError("No tabular file found inside zip archive.")

    def _extract_tabular_from_tar(self):
        """Extract the first supported tabular file from a TAR archive.

        Returns:
            pathlib.Path: Path to a temporary extracted file.

        Raises:
            NotTableError: If no supported tabular file exists in the archive.
        """
        with tarfile.open(self.main_file, mode="r:*") as archive:
            for member in archive.getmembers():
                if not member.isfile():
                    continue
                member_name = pathlib.Path(member.name)
                if member_name.suffix.lower() not in self.tabular_suffixes:
                    continue
                fileobj = archive.extractfile(member)
                if not fileobj:
                    continue
                return self._write_temp_file(fileobj.read(), member_name.suffix.lower())

        raise NotTableError("No tabular file found inside tar archive.")

    def _extract_tabular_from_gzip_single(self):
        """Extract content from a single-file GZIP archive.

        Returns:
            pathlib.Path: Path to a temporary extracted file.
        """
        inferred_suffix = pathlib.Path(self.main_file.stem).suffix.lower()
        if inferred_suffix not in self.tabular_suffixes:
            inferred_suffix = ".txt"

        with gzip_open(self.main_file, "rb") as source:
            content = source.read()
        return self._write_temp_file(content, inferred_suffix)

    def _write_temp_file(self, content, suffix):
        """Write bytes to a temporary file with a given suffix.

        Args:
            content (bytes): File content to persist.
            suffix (str): File extension to assign to the temporary file.

        Returns:
            pathlib.Path: Path to the created temporary file.
        """
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            return pathlib.Path(tmp.name)
    HATS_PROPERTIES_FILENAMES = {"hats.properties", "properties"}
