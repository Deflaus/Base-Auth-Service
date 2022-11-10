import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from models.postgres.base import BaseModel


class UUIDMixin(BaseModel):
    __abstract__ = True

    pk: uuid.UUID = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)


class CreatedAtUpdatedAtMixin(BaseModel):
    __abstract__ = True

    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
