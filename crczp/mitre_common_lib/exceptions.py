"""
Module containing exceptions.
All exceptions inherit from the ApiException class.
"""


class ApiException(Exception):
    """
    Base exception class for this project.
    All other exceptions inherit form it.
    """


class ImproperlyConfigured(ApiException):
    """
    Raised when application was not configured properly.
    """


class AuthenticationTokenMissing(ApiException):
    """
    Raised when the Authorization header is missing from the request.
    """
