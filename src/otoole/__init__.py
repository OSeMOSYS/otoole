# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound
import os
from yaml import SafeLoader, load
from datapackage import Package
from sqlalchemy import create_engine

try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources  # type: ignore

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = "unknown"
finally:
    del get_distribution, DistributionNotFound


def _read_file(open_file, ending):
    if ending == ".yaml" or ending == ".yml":
        contents = load(open_file, Loader=SafeLoader)
    else:
        contents = open_file.readlines()
    return contents


def read_packaged_file(filename: str, module_name: str = None):

    _, ending = os.path.splitext(filename)

    if module_name is None:
        with open(filename, "r") as open_file:
            contents = _read_file(open_file, ending)
    else:
        with resources.open_text(module_name, filename) as open_file:
            contents = _read_file(open_file, ending)

    return contents


def read_datapackage(filepath: str, sql: bool = False):
    """Open an OSeMOSYS datapackage

    Arguments
    ---------
    filepath : str
    sql : bool, default=False
    """
    if sql:
        engine = create_engine("sqlite:///{}".format(filepath))
        package = Package(storage="sql", engine=engine)
        package.infer()
    else:
        package = Package(filepath)

    return package
