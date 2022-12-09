import json
import logging
import os
from typing import Dict, List, Union

from datapackage import Package
from sqlalchemy import create_engine
from yaml import SafeLoader, load  # type: ignore

try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources  # type: ignore

logger = logging.getLogger(__name__)


def _read_file(open_file, ending):
    if ending == ".yaml" or ending == ".yml":
        contents = load(open_file, Loader=SafeLoader)  # typing: Dict
    elif ending == ".json":
        contents = json.load(open_file)  # typing: Dict
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


def create_name_mappings(
    config: Dict[str, Dict[str, Union[str, List]]], map_full_to_short: bool = True
) -> Dict:
    """Creates name mapping between full name and short name.

    Arguments
    ---------
    config : Dict[str, Dict[str, Union[str, List]]]
        Parsed user configuration file
    map_full_to_short: bool
        Map full name to short name if true, else map short name to full name

    Returns
    -------
    csv_to_excel Dict[str, str]
        Mapping of full name to shortened name

    """

    csv_to_excel = {}
    for name, params in config.items():
        try:
            csv_to_excel[name] = params["short_name"]
        except KeyError:
            if len(name) > 31:
                logger.info(f"{name} does not have a 'short_name'")
            continue

    if map_full_to_short:
        return csv_to_excel
    else:
        return {v: k for k, v in csv_to_excel.items()}
