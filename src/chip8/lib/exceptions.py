class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class OverflowException(Error):
    """Exception raised when memory overflow occurs.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)