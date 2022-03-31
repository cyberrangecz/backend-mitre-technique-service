import structlog
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from kypo.mitre_common_lib.exceptions import ApiException

# Create logger
LOG = structlog.get_logger()

def custom_exception_handler(exc, context):
    """Handle KYPO exceptions in a special way."""

    if isinstance(exc, ApiException):
        response = handle_kypo_exception(exc, context)
    else:
        # Call REST framework's default exception handler, to get the standard error response.
        # Handles only Django Errors.
        response = exception_handler(exc, context)

        if response is None:
            response = Response({
                'detail': str(exc),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    LOG.error(repr(exc), data=response.data if response else None, exc_info=True)
    return response


def handle_kypo_exception(exc, context):
    """Handle this project exceptions."""
    return Response({
        'detail': str(exc),
    }, status=status.HTTP_400_BAD_REQUEST)
