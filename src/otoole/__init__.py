# -*- coding: utf-8 -*-
import sys

from otoole.convert import convert, convert_results, read, read_results, write

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

convert = convert
convert_results = convert_results
read = read
write = write
read_results = read_results

__all__ = ["convert" "convert_results", "read", "write", "read_results"]
