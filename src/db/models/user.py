import typing

from sqlalchemy import Boolean, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel
from db.models.mixins import CreatedAtUpdatedAtMixin, UUIDMixin
from enums import UserRolesEnum

if typing.TYPE_CHECKING:
    from db.models.jwt_session import JwtSession


class User(BaseModel, UUIDMixin, CreatedAtUpdatedAtMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(length=255), nullable=False, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(length=255), default=None, nullable=True)
    email: Mapped[str | None] = mapped_column(String(length=255), default=None, nullable=True, unique=True)

    password: Mapped[str] = mapped_column(Text, nullable=False)

    role: Mapped[str] = mapped_column(Enum(UserRolesEnum), server_default=UserRolesEnum.STAFF.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    jwt_sessions: Mapped[typing.Iterable["JwtSession"]] = relationship(
        "JwtSession",
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )

    def __str__(self):
        return f"User #{self.uuid}"
