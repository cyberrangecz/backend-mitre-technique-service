"""
Module containing exceptions.
All exceptions inherit from the ApiException class.
"""


class ApiException(Exception):
    """
    Base exception class for this project.
    All other exceptions inherit form it.
    """
    pass


class ImproperlyConfigured(ApiException):
    """
    Raised when application was not configured properly.
    """
    pass
