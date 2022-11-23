import uuid
from enum import Enum

from schemas.base import BaseSchema


class UserRolesEnum(str, Enum):
    staff = "staff"
    admin = "admin"
    super_admin = "super_admin"


class UserBase(BaseSchema):
    username: str


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    pk: uuid.UUID
    role: UserRolesEnum
    email: str | None
    full_name: str | None
    is_active: bool

    class Config:
        orm_mode = True


class UserUpdate(BaseSchema):
    username: str | None
    full_name: str | None
