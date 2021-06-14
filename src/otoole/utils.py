import json
import os
from typing import Dict, List, Union

from datapackage import Package
from sqlalchemy import create_engine
from yaml import SafeLoader, load

try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources  # type: ignore


def _read_file(open_file, ending):
    if ending == ".yaml" or ending == ".yml":
        contents = load(open_file, Loader=SafeLoader)
    elif ending == ".json":
        contents = json.load(open_file)
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


def read_datapackage_schema_into_config(
    filepath: str, default_values: Dict
) -> Dict[str, Dict[str, Union[str, List]]]:
    with open(filepath, "r") as json_file:
        _, ending = os.path.splitext(filepath)
        schema = _read_file(json_file, ending)
    return extract_config(schema, default_values)


def extract_config(
    schema: Dict, default_values: Dict
) -> Dict[str, Dict[str, Union[str, List[str]]]]:

    config = {}  # type: Dict[str, Dict[str, Union[str, List[str]]]]
    for resource in schema["resources"]:

        name = resource["name"]
        if name == "default_values":
            continue

        dtype_mapping = {
            "number": "float",
            "string": "str",
            "float": "float",
            "integer": "int",
        }

        fields = resource["schema"]["fields"]
        dtype = [x["type"] for x in fields if x["name"] == "VALUE"][0]
        if (len(fields) == 1) & (fields[0]["name"] == "VALUE"):
            element_type = "set"
            config[name] = {"dtype": dtype_mapping[dtype], "type": element_type}
        else:
            element_type = "param"
            indices = [x["name"] for x in fields if x["name"] != "VALUE"]
            config[name] = {
                "type": element_type,
                "indices": indices,
                "dtype": dtype_mapping[dtype],
                "default": default_values[name],
            }
    return config
