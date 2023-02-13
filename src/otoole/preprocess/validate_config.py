"""Validation methods for the user configuration file."""

import logging
from typing import List, Optional, Union

from pydantic import BaseModel, root_validator, validator

logger = logging.getLogger(__name__)


class UserDefinedValue(BaseModel):
    """Represents any user defined value"""

    name: str
    type: str
    dtype: str
    defined_sets: Optional[List[str]]
    indices: Optional[List[str]]
    default: Optional[Union[int, float]]
    calculated: Optional[bool]
    short_name: Optional[str]

    @validator("type")
    @classmethod
    def check_param_type(cls, value, values):
        if value not in ["param", "result", "set"]:
            raise ValueError(
                f"{values['name']} -> Type must be 'param', 'result', or 'set'"
            )
        return value

    @validator("name", "short_name")
    @classmethod  # for linting purposes
    def check_name_for_spaces(cls, value):
        if " " in value:
            raise ValueError(f"{value} -> Name can not have spaces")
        return value

    @validator("name", "short_name")
    @classmethod
    def check_name_for_numbers(cls, value):
        if any(char.isdigit() for char in value):
            raise ValueError(f"{value} -> Name can not have digits")
        return value

    @validator("name", "short_name")
    @classmethod
    def check_name_for_special_chars(cls, value):
        # removed underscore from the recommeded special char list
        special_characters = " !\"#$%&'()*+,-./:;<=>?@[]^`{|}~"
        if any(c in special_characters for c in value):
            raise ValueError(
                f"{value} -> Name can not have special characters, except for underscores"
            )
        return value

    @root_validator(pre=True)
    @classmethod
    def check_name_length(cls, values):
        if len(values["name"]) > 31:
            if "short_name" not in values:
                raise ValueError(
                    f"{values['name']} -> Name is longer than 31 characters and no 'short_name' field provided"
                )
        if "short_name" in values:
            if len(values["short_name"]) > 31:
                raise ValueError(
                    f"{values['short_name']} -> Name is longer than 31 characters"
                )
        return values

    class Config:
        extra = "forbid"


class UserDefinedSet(UserDefinedValue):
    """Represents a parameter"""

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value, values):
        if value not in ["str", "int"]:
            raise ValueError(f"{values['name']} -> Value must be a 'str' or 'int'")
        return value


class UserDefinedParameter(UserDefinedValue):
    """Represents a user defined parameter"""

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value, values):
        if value not in ["float", "int"]:
            raise ValueError(f"{values['name']} -> Value must be an 'int' or 'float'")
        return value

    @root_validator(pre=True)
    @classmethod
    def check_required_inputs(cls, values):
        required = ["default", "defined_sets", "indices"]
        if not all(req in values for req in required):
            raise ValueError(
                f"{values['name']} -> Missing one of required fields ('default', 'defined_sets', 'indices')"
            )
        return values

    @root_validator(pre=True)
    @classmethod
    def check_index_in_set(cls, values):
        if not all(i in values["defined_sets"] for i in values["indices"]):
            raise ValueError(f"{values['name']} -> Index not in user supplied sets")
        return values

    @root_validator(pre=True)
    @classmethod
    def check_dtype_default(cls, values):
        dtype_input = values["dtype"]
        dtype_default = type(values["default"]).__name__
        if dtype_input != dtype_default:
            # allow ints to be cast as floats
            if not ((dtype_default == "int") and (dtype_input == "float")):
                raise ValueError(
                    f"{values['name']} -> User dtype is {dtype_input} while default value dtype is {dtype_default}"
                )
        return values


class UserDefinedResult(UserDefinedValue):
    """Represents a parameter"""

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value, values):
        if value not in ["float", "int"]:
            raise ValueError(f"{values['name']} -> Value must be an 'int' or 'float'")
        return value

    @root_validator(pre=True)
    @classmethod
    def check_required_inputs(cls, values):
        required = ["default", "defined_sets", "indices", "calculated"]
        if not all(req in values for req in required):
            raise ValueError(
                f"{values['name']} -> Missing one of required fields ('default', 'defined_sets', 'indices', calculated)"
            )
        return values

    @root_validator(pre=True)
    @classmethod
    def check_index_in_set(cls, values):
        if not all(i in values["defined_sets"] for i in values["indices"]):
            raise ValueError(f"{values['name']} -> Index not in user supplied sets")
        return values

    @root_validator(pre=True)
    @classmethod
    def check_dtype_default(cls, values):
        dtype_input = values["dtype"]
        dtype_default = type(values["default"]).__name__
        if dtype_input != dtype_default:
            # allow ints to be cast as floats
            if not ((dtype_default == "int") and (dtype_input == "float")):
                raise ValueError(
                    f"{values['name']} -> User dtype is {dtype_input} while default value dtype is {dtype_default}"
                )
        return values
