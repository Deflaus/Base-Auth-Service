from schemas.base import BaseSchema
from schemas.user import UserRolesEnum


class TokenPairSchema(BaseSchema):
    access: str
    refresh: str


class SignInSchema(BaseSchema):
    username: str
    password: str


class TokenPayload(BaseSchema):
    sub: str
    role: UserRolesEnum
    exp: int
