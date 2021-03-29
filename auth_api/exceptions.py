from flask import Response
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException


class RequestValidationError(HTTPException):
    code = 400

    def __init__(self, e: ValidationError):
        self.response = Response(status=self.code, response=str(e))


class AlreadyExistsError(HTTPException):
    code = 409
