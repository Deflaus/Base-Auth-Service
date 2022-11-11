import uuid
from datetime import timedelta

import aioredis
from pydantic import BaseModel, Field

from core.key_schema import BaseKeySchema
from db.redis import get_redis
from utils.json import OrjsonConfig


class NotFoundError(Exception):
    """Raised when a query found no results."""


class RedisKeySchema(BaseKeySchema):
    delimiter = ":"


class RedisBaseModel(BaseModel):
    pk: uuid.UUID = Field(default_factory=uuid.uuid4)
    _key_schema: RedisKeySchema | None = None
    _database: aioredis.Redis = get_redis()

    @classmethod
    def db(cls) -> aioredis.Redis:
        return cls._database

    @classmethod
    def _make_key(cls, pk: uuid.UUID) -> str:
        if cls._key_schema is None:
            return str(pk)

        return cls._key_schema.get_key(pk)

    def _key(self) -> str:
        return self._make_key(self.pk)

    @classmethod
    async def delete(cls, pk: uuid.UUID):
        raise NotImplementedError

    @classmethod
    async def get(cls, pk: uuid.UUID) -> "RedisBaseModel":
        raise NotImplementedError

    async def save(self, pipeline: aioredis.client.Pipeline = None, expire_time: int = 0) -> "RedisBaseModel":
        raise NotImplementedError


class RedisJsonModel(RedisBaseModel):
    class Config(OrjsonConfig):
        pass

    @classmethod
    async def delete(cls, pk: uuid.UUID) -> int:
        return await cls.db().delete(cls._make_key(pk))

    @classmethod
    async def get(cls, pk: uuid.UUID) -> "RedisJsonModel":
        data = await cls.db().execute_command("JSON.GET", cls._make_key(pk), ".")
        if not data:
            raise NotFoundError

        obj = cls.parse_raw(data)
        return obj

    async def save(
        self, pipeline: aioredis.client.Pipeline = None, expire_time: int | timedelta = 0
    ) -> "RedisJsonModel":
        if pipeline is None:
            conn = self.db()
        else:
            conn = pipeline

        key = self._key()
        await conn.execute_command("JSON.SET", key, ".", self.json())
        if expire_time:
            await conn.expire(key, expire_time)

        return self
