"""Validation methods for the user configuration file."""

import os
from typing import List, Optional, Union

from pydantic import BaseModel, root_validator, validator
from yaml import SafeLoader, load

from otoole.exceptions import OtooleConfigFileError


def user_defined_sets(user_config):
    """Extracts user defined sets"""
    return [x for x, y in user_config.items() if y["type"] == "set"]


def capitalize(name: str) -> str:
    return name.upper()


class UserDefinedValue(BaseModel):
    """Represents any user defined value"""

    name: str
    param_type: str
    dtype: Union[str, int, float]

    @validator("name")
    @classmethod  # for linting purposes
    def check_name_for_spaces(cls, value):
        return value

    @validator("name")
    @classmethod
    def check_name_for_numbers(cls, value):
        # not sure if this one is actually needed
        return value

    @validator("name")
    @classmethod
    def check_name_length(cls, value):
        # log warning for +31 char names
        return value

    @validator("param_type")
    @classmethod
    def check_param_type(cls, value):
        if value not in ["param", "result", "set"]:
            raise OtooleConfigFileError(
                param=value,
                message="Parameter type must be 'parameter', 'result', or 'set'",
            )
        return value


class UserDefinedParameter(UserDefinedValue):
    """Represents a user defined parameter"""

    user_defined_sets: List[str]
    indices: List[str]
    default: Union[int, float]
    short_name: Optional[str]

    _capitalize_indices = validator("indices", allow_reuse=True, each_item=True)(
        capitalize
    )

    @root_validator(pre=False)
    @classmethod
    def check_index_in_set(cls, values):
        if not all(i in values["user_defined_sets"] for i in values["indices"]):
            raise OtooleConfigFileError(
                param=values["name"], message="Index not in user supplied sets"
            )
        return values

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value):
        # check for int or float
        return value


class UserDefinedResult(UserDefinedValue):
    """Represents a parameter"""

    user_defined_sets: List[str]
    indices: List[str]
    default: Union[int, float]
    calculated: bool

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value):
        # check for int or float
        return value

    # probably a way to reuse this from UserDefinedParameter
    @root_validator(pre=False)
    @classmethod
    def check_index_in_set(cls, values):
        if not all(i in values["user_defined_sets"] for i in values["indices"]):
            raise OtooleConfigFileError(
                param=values["name"], message="Index not in user supplied sets"
            )
        return values


class UserDefinedSet(UserDefinedValue):
    """Represents a parameter"""

    @validator("name", pre=True)
    @classmethod
    def capitalize_name(cls, name: str) -> str:
        return name.upper()

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value):
        # check standard sets
        # EMISSION, REGION ect...  -> str
        # MODE -> int
        # ...
        return value


#########################################################################
# JUST FOR TESTING.
# run "python src/otoole/preprocess/validate_config.py" to test
########################################################################

# from otoole.cli - will replace with _read_file(...) later
cwd = os.path.abspath(os.path.dirname(__file__))
config_filepath = os.path.join(cwd, "config.yaml")
with open(config_filepath, "r") as open_file:
    config = load(open_file, Loader=SafeLoader)

user_defined_sets = user_defined_sets(config)

param = UserDefinedParameter(
    user_defined_sets=user_defined_sets,
    name="TechnologyFromStorage",
    indices=["REGION", "TECHNOLOGY", "STORAGE", "MODE_OF_OPERATION"],
    param_type="param",
    dtype="float",
    default=0,
)
print(param)

#########################################################################
# JUST FOR REFERENCE.
########################################################################

# class UserDefinedParameter(BaseModel):
#     """Represents a parameter, result, or set."""

#     name: str
#     indices: Optional[List[str]]
#     param_type: str
#     dtype: str
#     default: Optional[Union[int, float]]
#     calculated: Optional[bool]

#     @root_validator(pre=True)
#     def check_for_default_value(cls, values):
#         if (values['param_type'] == 'result') | (values['param_type'] == 'param'):
#             if 'default' not in values:
#                 raise OtooleConfigFileError(
#                     param=values['name'],
#                     message="Must have default value"
#                 )
#         return values

#     @root_validator('param_type','calculated', pre=True)
#     def check_for_calculated(cls, values):
#         print(values)
#         if values['param_type'] == 'result':
#             if not type(values['calculated']) is bool:
#                 raise OtooleConfigFileError(
#                     param=values['param_type'],
#                     message="Parameter type must be 'parameter', 'result', or 'set'"
#                 )
#         return values

#     @validator('param_type')
#     def check_param_type(cls, value):
#         if value not in ['param', 'result', 'set']:
#             raise OtooleConfigFileError(
#                 param=value,
#                 message="Parameter type must be 'parameter', 'result', or 'set'"
#             )
#         return value
