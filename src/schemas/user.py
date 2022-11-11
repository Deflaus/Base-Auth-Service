import uuid

from schemas.base import BaseSchema


class UserBase(BaseSchema):
    username: str


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    pk: uuid.UUID
    email: str | None
    full_name: str | None
    is_active: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseSchema):
    username: str | None
    full_name: str | None
