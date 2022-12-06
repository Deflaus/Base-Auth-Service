import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from models.postgres.mixins import CreatedAtUpdatedAtMixin, UUIDMixin
from models.postgres.user import User


class JwtSession(UUIDMixin, CreatedAtUpdatedAtMixin):
    __tablename__ = "jwt_sessions"

    user_pk: uuid.UUID = Column(UUID(as_uuid=True), ForeignKey("users.pk"), index=True, nullable=False)
    user: User = relationship("User", backref="jwt_sessions")
    refresh_token: str = Column(String, nullable=False, unique=True)
    expires_at: datetime = Column(DateTime, nullable=False)
    is_denied: bool = Column(Boolean, default=False, nullable=False)

    def __str__(self) -> str:
        return f"JWT session for user #{self.user_pk}"
