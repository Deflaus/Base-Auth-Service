import aioredis

from core.settings import settings


def get_db(url: str = settings().REDIS_DSN) -> aioredis.Redis:
    return aioredis.from_url(url, encoding="utf-8", decode_responses=True)
