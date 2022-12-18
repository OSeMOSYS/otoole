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


class OtooleExcelNameMismatchError(OtooleException):
    """Name mismatch between config and excel tabs."""

    def __init__(
        self, excel_name: str, message: str = "Excel tab name not found in config file"
    ) -> None:
        self.excel_name = excel_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.excel_name} -> {self.message}"
