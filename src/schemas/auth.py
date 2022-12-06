from pydantic import BaseModel
from schemas.user import UserRolesEnum


class BaseTokenPayload(BaseModel):
    sub: str
    exp: int


class AccessTokenPayload(BaseTokenPayload):
    role: UserRolesEnum


class RefreshTokenPayload(BaseTokenPayload):
    pass
