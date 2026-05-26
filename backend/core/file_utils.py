from pathlib import Path

MULTIPART_EXTENSIONS = (
    ".tar.gz",
    ".tar.bz2",
    ".tar.xz",
)


def get_file_extension(filename: str) -> str:
    """Return normalized file extension, preserving common multipart extensions."""
    basename = Path(filename).name.lower()

    for extension in MULTIPART_EXTENSIONS:
        if basename.endswith(extension):
            return extension

    return Path(basename).suffix.lower()
