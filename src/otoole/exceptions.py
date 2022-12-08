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
    def __init__(self, param: str, message: str) -> None:
        self.param = param
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"{self.param} -> {self.message}"
