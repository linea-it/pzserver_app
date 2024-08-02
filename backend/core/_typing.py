from os import PathLike
from typing import Union

FilePath = Union[str, "PathLike[str]"]
Column = Union[str, int]
OpInt = Union[int, None]
OpStr = Union[str, None]
