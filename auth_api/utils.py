from typing import Type, TypeVar

import pydantic
from pydantic import BaseModel, ValidationError

from exceptions import RequestValidationError


def validate_password(password):
    # check that password is good enough
    return False, None


BM = TypeVar("BM", bound=BaseModel)


def parse_obj_raise(model_type: Type[BM], data: dict) -> BM:
    try:
        user_data = pydantic.parse_obj_as(model_type, data)
        return user_data
    except ValidationError as e:
        raise RequestValidationError(e)
