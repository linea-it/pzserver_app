from core.file_utils import get_file_extension


def test_get_file_extension_for_simple_extension():
    assert get_file_extension("catalog.csv") == ".csv"


def test_get_file_extension_for_multipart_extension():
    assert get_file_extension("catalog.tar.gz") == ".tar.gz"


def test_get_file_extension_is_case_insensitive():
    assert get_file_extension("CATALOG.TAR.GZ") == ".tar.gz"
