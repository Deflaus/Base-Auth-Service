import datetime as dt
import typing
import uuid as _uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.models.base import BaseModel
from db.models.mixins import CreatedAtUpdatedAtMixin, UUIDMixin

if typing.TYPE_CHECKING:
    from db.models.user import User


class JwtSession(BaseModel, UUIDMixin, CreatedAtUpdatedAtMixin):
    __tablename__ = "jwt_sessions"

    user_uuid: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.uuid", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user: Mapped["User"] = relationship("User", back_populates="jwt_sessions")

    refresh_token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    expires_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_denied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    def __str__(self) -> str:
        return f"JWT session of user #{self.user_uuid}"
