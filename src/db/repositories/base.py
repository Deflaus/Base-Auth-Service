import typing
import uuid as _uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_session
from db.redis import AsyncRedis, get_redis
from schemas.base import RedisKeySchema, RedisModelSchema


class BaseDatabaseRepository:
    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        self._session = session


class BaseRedisRepository:
    _model_schema: typing.Type[RedisModelSchema]
    _key_schema: RedisKeySchema

    def __init__(self, redis_client: AsyncRedis = Depends(get_redis)) -> None:
        self._redis_client = redis_client

    async def get(self, pk: _uuid.UUID) -> RedisModelSchema | None:
        value = await self._redis_client.get(self._key_schema.get_key(pk))
        if value is None:
            return None

        return self._model_schema.model_validate_json(value)

    async def save(self, instance: RedisModelSchema, expire_seconds: int | None = None) -> None:
        if not isinstance(instance, self._model_schema):
            raise ValueError("Instance is not instance of repository model schema")

        instance_key = self._key_schema.get_key(instance.pk)
        await self._redis_client.set(name=instance_key, value=instance.model_dump_json())

        if expire_seconds:
            await self._redis_client.expire(name=instance_key, time=expire_seconds)

    async def delete(self, pk: _uuid.UUID) -> None:
        await self._redis_client.delete(self._key_schema.get_key(pk))
