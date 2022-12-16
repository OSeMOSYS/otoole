import json
import os
from typing import Dict, List, Union

from datapackage import Package
from pydantic import ValidationError
from sqlalchemy import create_engine

# from otoole.exceptions import OtooleConfigFileError
from yaml import SafeLoader, load  # type: ignore

from otoole.preprocess.validate_config_pydantic import (
    UserDefinedParameter,
    UserDefinedResult,
    UserDefinedSet,
)

try:
    import importlib.resources as resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as resources  # type: ignore


def _read_file(open_file, ending):
    if ending == ".yaml" or ending == ".yml":
        contents = load(open_file, Loader=UniqueKeyLoader)  # typing: Dict
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


def validate_config(config: Dict) -> None:
    """Validates user input data

    Arguments
    ---------
    config: Dict
        Read in user config yaml file

    Raises
    ------
    ValidationError
        If the user inputs are not valid
    """

    # For validating with json scheam
    """
    with open('src/otoole/preprocess/schema.json') as f:
        schema = load(f, Loader=SafeLoader)
    validate(config, schema=schema)
    """

    # For validating with pydantic
    config_flattened = format_config_for_validation(config)
    user_defined_sets = get_all_sets(config)

    try:
        for input_data in config_flattened:
            if input_data["type"] == "param":
                input_data["defined_sets"] = user_defined_sets
                UserDefinedParameter(**input_data)
            elif input_data["type"] == "result":
                input_data["defined_sets"] = user_defined_sets
                UserDefinedResult(**input_data)
            elif input_data["type"] == "set":
                UserDefinedSet(**input_data)
            else:
                # raise OtooleConfigFileError(
                #     param=input_data['name'],
                #     message=f"Type {input_data['type']} is not in the set ['parma','result',set']"
                # )
                raise ValueError(
                    f"{input_data['name']} -> Type {input_data['type']} is not in the set ['parma','result',set']"
                )
    except ValidationError as ex:
        print(ex)


def format_config_for_validation(config_in: Dict) -> List:
    """Formats config for validation function.

    Flattens dictionary to a list

    Arguments
    ---------
    config_in: Dict
        Read in user config yaml file

    Returns
    -------
    config_out: List

    Example
    -------
    >>> config_in
    >>> AccumulatedAnnualDemand:
          indices: [REGION,FUEL,YEAR]
          type: param
          dtype: float
          default: 0

    >>> config_out
    >>> [{
        name: AccumulatedAnnualDemand
        indices: [REGION,FUEL,YEAR]
        type: param
        dtype: float
        default: 0
        }, ... ]
    """
    config_out = []
    for name, data in config_in.items():
        flattened_data = {"name": name, **data}
        config_out.append(flattened_data)
    return config_out


class UniqueKeyLoader(SafeLoader):
    """YALM Loader to find duplicate keys

    Adapted from:
    https://stackoverflow.com/a/63215043/14961492
    """

    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in mapping:
                # raise OtooleConfigFileError(
                #     param=key,
                #     message='Value defined more than once'
                # )
                raise ValueError()
            mapping.append(key)
        return super().construct_mapping(node, deep)


def get_all_sets(config: Dict) -> List:
    """Extracts user defined sets"""
    return [x for x, y in config.items() if y["type"] == "set"]
