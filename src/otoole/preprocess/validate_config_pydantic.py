"""Validation methods for the user configuration file."""

import logging
from typing import List, Union

from pydantic import BaseModel, root_validator, validator

# from otoole.exceptions import OtooleConfigFileError

logger = logging.getLogger(__name__)


class UserDefinedValue(BaseModel):
    """Represents any user defined value"""

    name: str
    type: str
    dtype: str

    @validator("type")
    @classmethod
    def check_param_type(cls, value):
        if value not in ["param", "result", "set"]:
            # raise OtooleConfigFileError(
            #     param=value,
            #     message="Parameter type must be 'param', 'result', or 'set'",
            # )
            raise ValueError(
                f"{value} -> Parameter type must be 'param', 'result', or 'set'"
            )
        return value

    @validator("name")
    @classmethod  # for linting purposes
    def check_name_for_spaces(cls, value):
        if " " in value:
            # raise OtooleConfigFileError(
            #     param=value,
            #     message="Parameter name can not have spaces",
            # )
            raise ValueError(f"{value} -> Parameter name can not have spaces")
        return value

    @validator("name")
    @classmethod
    def check_name_for_numbers(cls, value):
        if any(char.isdigit() for char in value):
            # raise OtooleConfigFileError(
            #     param=value,
            #     message="Parameter name can not have digits",
            # )
            raise ValueError(f"{value} -> Parameter name can not have digits")
        return value

    @validator("name")
    @classmethod
    def check_name_for_special_chars(cls, value):
        # removed underscore from the recommeded special char list
        special_characters = " !\"#$%&'()*+,-./:;<=>?@[]^`{|}~"
        if any(c in special_characters for c in value):
            # raise OtooleConfigFileError(
            #     param=value,
            #     message="Parameter name can not have special characters",
            # )
            raise ValueError(
                f"{value} -> Parameter name can not have special characters"
            )
        return value

    # TODO: change this to a warning and check for short name
    @validator("name")
    @classmethod
    def check_name_length(cls, value):
        if len(value) > 31:
            logger.warning(f"{value} is longer than 31 characters")
            # raise OtooleConfigFileError(
            #     param=value,
            #     message="Name is longer than 31 characters",
            # )
            raise ValueError(f"{value} -> Longer than 31 characters")
        return value


class UserDefinedSet(UserDefinedValue):
    """Represents a parameter"""

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value):
        if value not in ["str", "int"]:
            # raise OtooleConfigFileError(
            #     param=value, message="Value must be a 'str' or 'int'"
            # )
            raise ValueError(f"{value} -> Value must be a 'str' or 'int'")
        return value


class UserDefinedParameter(UserDefinedValue):
    """Represents a user defined parameter"""

    defined_sets: List[str]
    indices: List[str]
    default: Union[int, float]

    @root_validator(pre=False)
    @classmethod
    def check_index_in_set(cls, values):
        if not all(i in values["defined_sets"] for i in values["indices"]):
            # raise OtooleConfigFileError(
            #     param=values["name"], message="Index not in user supplied sets"
            # )
            raise ValueError(f"{values['name']} -> Index not in user supplied sets")
        return values

    @root_validator(pre=False)
    @classmethod
    def check_dtype_default(cls, values):
        dtype_input = values["dtype"]
        dtype_default = type(values["default"]).__name__
        if dtype_input != dtype_default:
            # allow ints to be cast as floats
            if not ((dtype_default == "int") and (dtype_input == "float")):
                # raise OtooleConfigFileError(
                #     param=values['name'],
                #     message=f"User dtype is {dtype_input} while default value dtype is {dtype_default}"
                # )
                raise ValueError(
                    f"{values['name']} -> User dtype is {dtype_input} while default value dtype is {dtype_default}"
                )
        return values

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value):
        if value not in ["float", "int"]:
            # raise OtooleConfigFileError(
            #     param=value, message="Value must be an 'int' or 'float'"
            # )
            raise ValueError(f"{value} -> Value must be an 'int' or 'float'")
        return value


# might be a way to merge this with UserDefinedParameter
class UserDefinedResult(UserDefinedValue):
    """Represents a parameter"""

    defined_sets: List[str]
    indices: List[str]
    default: Union[int, float]
    calculated: bool

    @validator("dtype")
    @classmethod
    def check_dtype(cls, value):
        if value not in ["float", "int"]:
            # raise OtooleConfigFileError(
            #     param=value, message="Value must be an 'int' or 'float'"
            # )
            raise ValueError(f"{value} -> Value must be an 'int' or 'float'")
        return value

    @root_validator(pre=False)
    @classmethod
    def check_index_in_set(cls, values):
        if not all(i in values["defined_sets"] for i in values["indices"]):
            # raise OtooleConfigFileError(
            #     param=values["name"], message="Index not in user supplied sets"
            # )
            raise ValueError(f"{values['name']} -> Index not in user supplied sets")
        return values

    @root_validator(pre=False)
    @classmethod
    def check_dtype_default(cls, values):
        dtype_input = values["dtype"]
        dtype_default = type(values["default"]).__name__
        if dtype_input != dtype_default:
            # allow ints to be cast as floats
            if not ((dtype_default == "int") and (dtype_input == "float")):
                # raise OtooleConfigFileError(
                #     param=values['name'],
                #     message=f"User dtype is {dtype_input} while default value dtype is {dtype_default}"
                # )
                raise ValueError(
                    f"{values['name']} -> User dtype is {dtype_input} while default value dtype is {dtype_default}"
                )
        return values
