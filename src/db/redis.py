import aioredis

from core.settings import settings


def get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings().REDIS_DSN, encoding="utf-8", decode_responses=True)
