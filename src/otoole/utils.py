import json
import logging
import os
from importlib.resources import files
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from pydantic import ValidationError
from yaml import SafeLoader, load  # type: ignore

from otoole.exceptions import OtooleConfigFileError, OtooleDeprecationError
from otoole.preprocess.validate_config import (
    UserDefinedParameter,
    UserDefinedResult,
    UserDefinedSet,
    UserDefinedValue,
)

logger = logging.getLogger(__name__)


def _read_file(open_file, ending):
    if ending == ".yaml" or ending == ".yml":
        contents = load(open_file, Loader=UniqueKeyLoader)  # typing: Dict[str, Any]
    elif ending == ".json":
        contents = json.load(open_file)  # typing: Dict
    else:
        contents = open_file.readlines()
    return contents


def read_packaged_file(filename: str, module_name: Optional[str] = None):

    _, ending = os.path.splitext(filename)

    if module_name is None:
        with open(filename, "r") as open_file:
            contents = _read_file(open_file, ending)
    else:
        with files(module_name).joinpath(filename).open("r") as open_file:
            contents = _read_file(open_file, ending)

    return contents


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

    # For validating with pydantic
    config_flattened = format_config_for_validation(config)
    user_defined_sets = get_all_sets(config)

    errors = []
    for input_data in config_flattened:
        try:
            if "type" not in input_data:
                UserDefinedValue(**input_data)
            elif input_data["type"] == "param":
                input_data["defined_sets"] = user_defined_sets
                UserDefinedParameter(**input_data)
            elif input_data["type"] == "result":
                input_data["defined_sets"] = user_defined_sets
                UserDefinedResult(**input_data)
            elif input_data["type"] == "set":
                UserDefinedSet(**input_data)
            else:
                # have pydantic raise an error
                UserDefinedValue(
                    name=input_data["name"],
                    type=input_data["type"],
                    dtype=input_data["dtype"],
                )
        except ValidationError as ex:
            errors_caught = [x["msg"] for x in ex.errors()]
            errors.extend(errors_caught)

    if errors:
        error_message = "\n".join(errors)
        raise OtooleConfigFileError(message=f"\n{error_message}")


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


def read_deprecated_datapackage(datapackage: str) -> str:
    """Checks filepath for CSVs if a datapackage is provided

    Arguments
    ---------
    datapackage: str
        Location of input datapackge

    Returns
    -------
    input_csvs: str
        Location of input csv files

    Raises
    ------
    OtooleDeprecationError
        If no 'data/' directory is found
    """

    input_csvs = os.path.join(os.path.dirname(datapackage), "data")
    if os.path.exists(input_csvs):
        return input_csvs
    else:
        raise OtooleDeprecationError(
            resource="datapackage.json",
            message="datapackage format no longer supported and no csv data found",
        )


def get_packaged_resource(
    input_data: Dict[str, pd.DataFrame], param: str
) -> List[Dict[str, Any]]:
    """Gets input parameter data and formats it as a dictionary

    Arguments
    ---------
    input_data : Dict[str, pd.DataFrame]
        Internal datastore for otoole input data
    param : str
        Name of OSeMOSYS parameter

    Returns
    -------
    List[Dict[str,any]]
        List of all rows in the df, where each dictionary is the column
        name, followed by the value in that row

    Example
    -------
    >>> get_packaged_resource(input_data, "InputActivityRatio")
    >>> [{'REGION': 'SIMPLICITY',
        'TECHNOLOGY': 'RIVWATAGR',
        'FUEL': 'WATIN',
        'MODE_OF_OPERATION': 1,
        'YEAR': 2020,
        'VALUE': 1.0}]
    """
    return input_data[param].reset_index().to_dict(orient="records")


class UniqueKeyLoader(SafeLoader):
    """YALM Loader to find duplicate keys

    This loader will treat lowercase and uppercase keys as the same. Meaning,
    the keys "SampleKey" and "SAMPLEKEY" are considered the same.

    Raises
    ------
    ValueError
        If a key is defined more than once.

    Adapted from:
    https://stackoverflow.com/a/63215043/14961492
    """

    def construct_mapping(self, node, deep=False):
        mapping = []
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            key = key.upper()
            if key in mapping:
                raise ValueError(f"{key} -> defined more than once")
            mapping.append(key)
        return super().construct_mapping(node, deep)


def get_all_sets(config: Dict) -> List:
    """Extracts user defined sets"""
    return [x for x, y in config.items() if y["type"] == "set"]
