from schemas.base import BaseSchema


class TokenPairSchema(BaseSchema):
    access: str
    refresh: str


class SignInRequestSchema(BaseSchema):
    username: str
    password: str


class TokenPayload(BaseSchema):
    user_pk: str
    exp: int
