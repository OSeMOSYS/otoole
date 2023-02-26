# -*- coding: utf-8 -*-
import sys

from otoole.input import Context
from otoole.read_strategies import ReadCsv, ReadDatafile, ReadExcel, ReadMemory
from otoole.results.results import ReadCbc, ReadCplex, ReadGurobi
from otoole.write_strategies import WriteCsv, WriteDatafile, WriteExcel

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


__all__ = [
    "Context",
    "ReadCbc",
    "ReadCsv",
    "ReadCplex",
    "ReadDatafile",
    "ReadExcel",
    "ReadGurobi",
    "ReadMemory",
    "WriteCsv",
    "WriteDatafile",
    "WriteExcel",
]
