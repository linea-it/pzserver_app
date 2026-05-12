import pathlib
import tarfile
import tempfile
import zipfile
from gzip import open as gzip_open

import pandas as pd
import pyarrow.parquet as pq
from core.product_handle import CsvHandle, FileHandle, NotTableError, ProductHandle, TxtHandle


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

    def collect(self):
        """Collect preview rows, column names, and total row count.

        Returns:
            dict: A dictionary with keys `preview_df`, `columns`, and `n_rows`.

        Raises:
            NotTableError: If no tabular content can be extracted from the file.
        """
        suffix = self.main_file.suffix.lower()
        if suffix in {".zip", ".tar", ".gz"}:
            return self._collect_from_compressed_main_file()
        return self._collect_from_path(self.main_file)

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
        suffix = self.main_file.suffix.lower()

        if suffix == ".zip":
            extracted_path = self._extract_tabular_from_zip()
        elif suffix in {".tar", ".gz"} and tarfile.is_tarfile(self.main_file):
            extracted_path = self._extract_tabular_from_tar()
        elif suffix == ".gz":
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
        with tarfile.open(self.main_file) as archive:
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
