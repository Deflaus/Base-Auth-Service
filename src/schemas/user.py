import uuid
from enum import Enum

from pydantic import BaseModel


class UserRolesEnum(str, Enum):
    staff = "staff"
    admin = "admin"
    super_admin = "super_admin"


class UserBase(BaseModel):
    username: str

    class Config:
        orm_mode = True


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    pk: uuid.UUID
    role: UserRolesEnum
    email: str | None
    full_name: str | None
    is_active: bool


class UserUpdate(UserBase):
    username: str | None
    full_name: str | None
