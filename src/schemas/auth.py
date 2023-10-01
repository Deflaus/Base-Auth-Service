import datetime as dt
import uuid

from pydantic import BaseModel


class SignInInputSchema(BaseModel):
    username: str
    password: str


class SignUpInputSchema(BaseModel):
    username: str
    password: str
    full_name: str | None = None
    email: str | None = None


class _UserJwtSessionBaseSchema(BaseModel):
    user_uuid: uuid.UUID
    refresh_token: str
    expires_at: dt.datetime


class UserJwtSessionCreateSchema(_UserJwtSessionBaseSchema):
    pass


class _BaseTokenPayloadSchema(BaseModel):
    sub: str
    exp: int


class AccessTokenPayloadSchema(_BaseTokenPayloadSchema):
    pass


class RefreshTokenPayloadSchema(_BaseTokenPayloadSchema):
    pass


class TokenPairOutputSchema(BaseModel):
    refresh_token: str
    access_token: str


class AccessTokenOutputSchema(BaseModel):
    access_token: str


class RefreshTokenOutputSchema(BaseModel):
    refresh_token: str
