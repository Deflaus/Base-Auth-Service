from calendar import timegm
from datetime import datetime

from pydantic import validator

from models.redis.base import RedisJsonModel, RedisKeySchema


class JwtPublicKey(RedisJsonModel):
    _key_schema: RedisKeySchema = RedisKeySchema(prefix="jwt_public_key")
    public_key: str


class RefreshToken(RedisJsonModel):
    _key_schema: RedisKeySchema = RedisKeySchema(prefix="refresh_token")
    token: str
    created_at: int = None  # type: ignore

    @validator("created_at", pre=True, always=True)
    def default_created_at(cls, value: int | None) -> int:
        return value or timegm(datetime.now().utctimetuple())
