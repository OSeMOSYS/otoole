"""Validation methods for the user configuration file."""

import json
import os
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, TypedDict

import yaml
from jsonschema import validate

cwd = os.path.abspath(os.path.dirname(__file__))
config_file = os.path.join(cwd, "config.yaml")
datapackage_file = os.path.join(cwd, "datapackage.json")

# get schema
with open(config_file, "r") as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

with open(datapackage_file, "r") as f:
    datapackage = json.load(f)

dp = datapackage["resources"]


def get_schema_param_type(
    fields: List[Dict[str, str]]
) -> Tuple[Dict[str, List[str]], str]:
    if len(fields) == 1:
        return ({"enum": ["set"]}, "array")
    else:
        types = {"enum": ["param", "result"]}
        return (types, "array")


def get_schema_dtype(fields: List[Dict[str, str]]) -> Optional[str]:
    dtype = None
    for field in fields:
        if field["name"] == "VALUE":
            dtype = field["type"]
    return dtype


def get_schema_indices(fields: List[Dict[str, str]]) -> Optional[Dict[str, List[str]]]:
    indices = []
    for field in fields:
        if field["name"] != "VALUE":
            indices.append(field["name"])
    if not indices:
        return None
    return {"enum": indices}


dict_type = TypedDict("dict_type", {"type": str, "properties": Dict})

schema: Dict = defaultdict()
schema["type"] = "object"
schema["properties"] = defaultdict()
for item in dp:
    name = item["name"]
    if name == "default_values":
        continue
    param, param_dtype = get_schema_param_type(item["schema"]["fields"])
    dtype = get_schema_dtype(item["schema"]["fields"])
    indices = get_schema_indices(item["schema"]["fields"])

    schema["properties"][name] = defaultdict()
    schema["properties"][name]["type"] = "object"
    schema["properties"][name]["properties"] = {}
    schema["properties"][name]["properties"]["default"] = defaultdict()
    schema["properties"][name]["properties"]["default"]["type"] = dtype
    schema["properties"][name]["properties"]["param"] = defaultdict()
    schema["properties"][name]["properties"]["param"]["anyof"] = defaultdict()
    schema["properties"][name]["properties"]["param"]["anyof"] = [{"pattern": param}]
    schema["properties"][name]["properties"]["default"] = defaultdict()
    schema["properties"][name]["properties"]["default"]["type"] = dtype
    if indices:
        schema["properties"][name]["properties"]["indices"] = defaultdict()
        schema["properties"][name]["properties"]["indices"]["type"] = "array"
        schema["properties"][name]["properties"]["indices"]["items"] = indices
    schema["properties"][name]["required"] = ["param"]

config_updated: Dict = defaultdict()
for param, param_data in config.items():
    config_updated[param] = defaultdict()
    for data_name, data in param_data.items():
        if data_name == "type":
            name = "param"
        else:
            name = data_name
        config_updated[param][name] = data

validate(config_updated, schema=datapackage)


# #########################################################
# # PYDANTIC
# #########################################################

# import os
# from typing import List, Optional, Union

# from pydantic import BaseModel, root_validator, validator
# from yaml import SafeLoader, load

# from otoole.exceptions import OtooleConfigFileError


# def user_defined_sets(user_config):
#     """Extracts user defined sets"""
#     return [x for x, y in user_config.items() if y["type"] == "set"]


# def capitalize(name: str) -> str:
#     return name.upper()


# class UserDefinedValue(BaseModel):
#     """Represents any user defined value"""

#     name: str
#     param_type: str
#     dtype: Union[str, int, float]

#     @validator("name")
#     @classmethod  # for linting purposes
#     def check_name_for_spaces(cls, value):
#         return value

#     @validator("name")
#     @classmethod
#     def check_name_for_numbers(cls, value):
#         # not sure if this one is actually needed
#         return value

#     @validator("name")
#     @classmethod
#     def check_name_length(cls, value):
#         # log warning for +31 char names
#         return value

#     @validator("param_type")
#     @classmethod
#     def check_param_type(cls, value):
#         if value not in ["param", "result", "set"]:
#             raise OtooleConfigFileError(
#                 param=value,
#                 message="Parameter type must be 'parameter', 'result', or 'set'",
#             )
#         return value


# class UserDefinedParameter(UserDefinedValue):
#     """Represents a user defined parameter"""

#     user_defined_sets: List[str]
#     indices: List[str]
#     default: Union[int, float]
#     short_name: Optional[str]

#     _capitalize_indices = validator("indices", allow_reuse=True, each_item=True)(
#         capitalize
#     )

#     @root_validator(pre=False)
#     @classmethod
#     def check_index_in_set(cls, values):
#         if not all(i in values["user_defined_sets"] for i in values["indices"]):
#             raise OtooleConfigFileError(
#                 param=values["name"], message="Index not in user supplied sets"
#             )
#         return values

#     @validator("dtype")
#     @classmethod
#     def check_dtype(cls, value):
#         # check for int or float
#         return value


# class UserDefinedResult(UserDefinedValue):
#     """Represents a parameter"""

#     user_defined_sets: List[str]
#     indices: List[str]
#     default: Union[int, float]
#     calculated: bool

#     @validator("dtype")
#     @classmethod
#     def check_dtype(cls, value):
#         # check for int or float
#         return value

#     # probably a way to reuse this from UserDefinedParameter
#     @root_validator(pre=False)
#     @classmethod
#     def check_index_in_set(cls, values):
#         if not all(i in values["user_defined_sets"] for i in values["indices"]):
#             raise OtooleConfigFileError(
#                 param=values["name"], message="Index not in user supplied sets"
#             )
#         return values


# class UserDefinedSet(UserDefinedValue):
#     """Represents a parameter"""

#     @validator("name", pre=True)
#     @classmethod
#     def capitalize_name(cls, name: str) -> str:
#         return name.upper()

#     @validator("dtype")
#     @classmethod
#     def check_dtype(cls, value):
#         # check standard sets
#         # EMISSION, REGION ect...  -> str
#         # MODE -> int
#         # ...
#         return value

# #########################################################################
# # JUST FOR TESTING.
# # run "python src/otoole/preprocess/validate_config.py" to test
# ########################################################################

# # from otoole.cli - will replace with _read_file(...) later
# cwd = os.path.abspath(os.path.dirname(__file__))
# config_filepath = os.path.join(cwd, "config.yaml")
# with open(config_filepath, "r") as open_file:
#     config = load(open_file, Loader=SafeLoader)

# user_defined_sets = user_defined_sets(config)

# param = UserDefinedParameter(
#     user_defined_sets=user_defined_sets,
#     name="TechnologyFromStorage",
#     indices=["REGION", "TECHNOLOGY", "STORAGE", "MODE_OF_OPERATION"],
#     param_type="param",
#     dtype="float",
#     default=0,
# )
# print(param)
