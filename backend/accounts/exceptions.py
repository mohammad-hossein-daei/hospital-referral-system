# accounts/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and isinstance(exc, NotAuthenticated):
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return response