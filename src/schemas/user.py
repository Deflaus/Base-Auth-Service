import uuid as _uuid

from enums import UserRolesEnum
from schemas.base import BaseOrmSchema


class _UserBaseSchema(BaseOrmSchema):
    username: str
    full_name: str | None = None
    email: str | None = None
    role: UserRolesEnum
    is_active: bool


class UserOutputSchema(_UserBaseSchema):
    uuid: _uuid.UUID


class UserCreateSchema(_UserBaseSchema):
    password: str


class UserChangeSchema(BaseOrmSchema):
    username: str | None = None
    full_name: str | None = None
    email: str | None = None
