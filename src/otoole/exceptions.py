class OtooleException(Exception):
    """Base class for all otoole exceptions.

    """

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
