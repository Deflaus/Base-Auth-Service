import uuid
from datetime import datetime

from pydantic import BaseModel


class JwtSessionBase(BaseModel):
    refresh_token: str
    user_pk: uuid.UUID
    expires_at: datetime

    class Config:
        orm_mode = True


class JwtSessionGet(JwtSessionBase):
    created_at: datetime
    is_denied: bool


class JwtSessionCreate(JwtSessionBase):
    pass
