"""Validation methods for the user configuration file."""

import logging
from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# from pydantic import FieldValidationInfo


logger = logging.getLogger(__name__)


class UserDefinedValue(BaseModel):
    """Represents any user defined value"""

    model_config = ConfigDict(extra="forbid")

    name: str
    type: str
    dtype: str
    defined_sets: Optional[List[str]] = None
    indices: Optional[List[str]] = None
    default: Optional[Union[int, float]] = None
    calculated: Optional[bool] = None
    short_name: Optional[str] = None

    @field_validator("type")
    @classmethod
    def check_param_type(cls, value, info):
        if value not in ["param", "result", "set"]:
            raise ValueError(
                f"{info.field_name} -> Type must be 'param', 'result', or 'set'"
            )
        return value

    @field_validator("name", "short_name")
    @classmethod  # for linting purposes
    def check_name_for_spaces(cls, value):
        if " " in value:
            raise ValueError(f"{value} -> Name can not have spaces")
        return value

    @field_validator("name", "short_name")
    @classmethod
    def check_name_for_numbers(cls, value):
        if any(char.isdigit() for char in value):
            raise ValueError(f"{value} -> Name can not have digits")
        return value

    @field_validator("name", "short_name")
    @classmethod
    def check_name_for_special_chars(cls, value):
        # removed underscore from the recommeded special char list
        special_characters = " !\"#$%&'()*+,-./:;<=>?@[]^`{|}~"
        if any(c in special_characters for c in value):
            raise ValueError(
                f"{value} -> Name can not have special characters, except for underscores"
            )
        return value

    @model_validator(mode="before")
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


class UserDefinedSet(UserDefinedValue):
    """Represents a set"""

    @field_validator("dtype")
    @classmethod
    def check_dtype(cls, value, info):
        if value not in ["str", "int"]:
            raise ValueError(f"{info.field_name} -> Value must be a 'str' or 'int'")
        return value


class UserDefinedParameter(UserDefinedValue):
    """Represents a parameter"""

    @field_validator("dtype")
    @classmethod
    def check_dtype(cls, value, info):
        if value not in ["float", "int"]:
            raise ValueError(f"{info.field_name} -> Value must be an 'int' or 'float'")
        return value

    @model_validator(mode="before")
    @classmethod
    def check_required_inputs(cls, values):
        required = ["default", "defined_sets", "indices"]
        if not all(req in values for req in required):
            raise ValueError(
                f"{values['name']} -> Missing one of required fields ('default', 'defined_sets', 'indices')"
            )
        return values

    @model_validator(mode="after")
    def check_index_in_set(self):
        if not all(i in self.defined_sets for i in self.indices):
            raise ValueError(f"{self.name} -> Index not in user supplied sets")
        return self

    @model_validator(mode="after")
    def check_dtype_default(self):
        dtype_input = self.dtype
        dtype_default = type(self.default).__name__
        if dtype_input != dtype_default:
            # allow ints to be cast as floats
            if not ((dtype_default == "int") and (dtype_input == "float")):
                raise ValueError(
                    f"{self.name} -> User dtype is {dtype_input} while default value dtype is {dtype_default}"
                )
        return self


class UserDefinedResult(UserDefinedValue):
    """Represents a result"""

    @field_validator("dtype")
    @classmethod
    def check_dtype(cls, value, info):
        if value not in ["float", "int"]:
            raise ValueError(f"{info.field_name} -> Value must be an 'int' or 'float'")
        return value

    @model_validator(mode="before")
    @classmethod
    def check_required_inputs(cls, values):
        required = ["default", "defined_sets", "indices"]
        if not all(req in values for req in required):
            raise ValueError(
                f"{values['name']} -> Missing one of required fields ('default', 'defined_sets', 'indices')"
            )
        return values

    @model_validator(mode="before")
    @classmethod
    def check_deprecated_values(cls, values):
        deprecated = ["calculated", "Calculated"]
        for v in values:
            if v in deprecated:
                logger.info(
                    f"{values['name']} -> Config file field of '{v}' is deprecated. Remove '{v}' to suppress this warning."
                )
        return values

    @model_validator(mode="after")
    def check_index_in_set(self):
        if not all(i in self.defined_sets for i in self.indices):
            raise ValueError(f"{self.name} -> Index not in user supplied sets")
        return self

    @model_validator(mode="after")
    def check_dtype_default(self):
        dtype_input = self.dtype
        dtype_default = type(self.default).__name__
        if dtype_input != dtype_default:
            # allow ints to be cast as floats
            if not ((dtype_default == "int") and (dtype_input == "float")):
                raise ValueError(
                    f"{self.name} -> User dtype is {dtype_input} while default value dtype is {dtype_default}"
                )
        return self
