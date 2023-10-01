import functools
import typing

from redis.asyncio import Redis, from_url

from settings import get_settings

AsyncRedis: typing.TypeAlias = Redis


@functools.lru_cache
def get_redis_connection() -> AsyncRedis:
    return from_url(get_settings().REDIS_DSN, encoding="utf-8", decode_responses=True)


async def get_redis() -> typing.AsyncGenerator[AsyncRedis, None]:
    async with get_redis_connection() as redis:
        yield redis
