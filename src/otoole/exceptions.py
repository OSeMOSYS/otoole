from typing import List, Union


class OtooleException(Exception):
    """Base class for all otoole exceptions."""

    pass


class OtooleValidationError(OtooleException):
    """Input data is invalid

    Arguments
    ---------
    resource : str
        Name of the resource which is invalid
    message : str
        Error message
    """

    def __init__(self, resource, message):
        self.resource = resource
        self.message = message


class OtooleRelationError(OtooleException):
    """Relations between input data is not correct

    Arguments
    ---------
    resource : str
        Name of the resource which is invalid
    foreign_resource : str
        Name of the resource which is invalid
    message : str
        Error message
    """

    def __init__(self, resource, foreign_resource, message):
        self.resource = resource
        self.foreign_resource = foreign_resource
        self.message = message


class OtooleConfigFileError(OtooleException):
    """Config file validation error

    Arguments
    ---------
    message: str
        Message to display to users
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.message}"


class OtooleExcelNameLengthError(OtooleException):
    """Invalid tab name for writing to Excel."""

    def __init__(
        self,
        name: str,
        message: str = "Parameter name must be less than 31 characters when writing to Excel",
    ) -> None:
        self.name = name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.name} -> {self.message}"


class OtooleNameMismatchError(OtooleException):
    """Names not consistent between read in data and config file"""

    def __init__(
        self,
        name: Union[List, str],
    ) -> None:
        if isinstance(name, list):
            self.message = "Names not consistent between data and config file"
            self.name = ", ".join(sorted(name))
        elif isinstance(name, str):
            self.name = name
            self.message = "Name not consistent between data and config file"
        else:
            raise TypeError("Incorrect type passed to OtooleNameMismatchError")
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}:\n\n{self.name}.\n\nUpdate config or data with matching names."


class OtooleDeprecationError(OtooleException):
    """New version of otoole does drops this feature support

    Arguments
    ---------
    resource : str
        Name of the resource which is invalid
    message : str
        Error message
    """

    def __init__(self, resource, message):
        self.resource = resource
        self.message = message

    def __str__(self):
        return f"{self.resource} -> {self.message}"


class OtooleSetupError(OtooleException):
    """Setup data already exists

    Arguments
    ---------
    resource : str
        Name of the resource which is invalid
    message : str
        Error message
    """

    def __init__(
        self,
        resource,
        message="Data already exists. Delete file/directory or pass the --overwrite flag",
    ):
        self.resource = resource
        self.message = message

    def __str__(self):
        return f"{self.resource} -> {self.message}"


class OtooleIndexError(OtooleException):
    """Index data not consistent between data and config file

    Arguments
    ---------
    resource : str
        Name of the resource which is invalid
    config_indices: List[str]
        Indices from config file
    data_indices: List[str]
        Indices from input data
    """

    def __init__(self, resource, config_indices, data_indices):
        self.resource = resource
        self.config_indices = config_indices
        self.data_indices = data_indices
        self.message = "Indices inconsistent between config and data"

    def __str__(self):
        return f"{self.resource} -> {self.message}. Config indices are {self.config_indices}. Data indices are {self.data_indices}."


class OtooleError(OtooleException):
    """General purpose error

    Arguments
    ---------
    resource : str
        Name of the resource which is invalid
    message : str
        Error message
    """

    def __init__(self, resource, message):
        self.resource = resource
        self.message = message

    def __str__(self):
        return f"{self.resource} -> {self.message}"
