from enum import Enum
from typing import Literal, Union

from pydantic import BaseModel, EmailStr, Field, SecretStr

from blocks import guard


class UserIn(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=100)


class GrantTypes(str, Enum):
    PASSWORD = "password"
    REFRESH_TOKEN = "refresh_token"


class TokenInBase(BaseModel):
    grant_type: GrantTypes = Field(alias="grantType")


class TokenInPassword(BaseModel):
    email: EmailStr
    password: SecretStr
    grant_type: Literal[GrantTypes.PASSWORD]


class TokenInRefresh(BaseModel):
    refresh_token: str
    grant_type: Literal[GrantTypes.REFRESH_TOKEN]


TokenIn = Union[TokenInPassword, TokenInRefresh]


class TokenRevokeIn(BaseModel):
    token: str


class TokenGrantOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'
    expires: int = Field(default_factory=lambda: int(guard.access_lifespan.total_seconds()))
