import datetime as dt
import uuid as _uuid

from schemas.base import BaseOrmSchema


class JwtSessionCreateSchema(BaseOrmSchema):
    user_uuid: _uuid.UUID
    refresh_token: str
    expires_at: dt.datetime
