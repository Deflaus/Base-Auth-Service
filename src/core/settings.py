import uuid
from functools import lru_cache

from pydantic import BaseSettings, RedisDsn, SecretStr


class Settings(BaseSettings):
    ENVIRONMENT: str = "local"
    REDIS_DSN: RedisDsn | str = "redis://0.0.0.0:6379/"
    PUBLIC_KEY_PK: uuid.UUID = uuid.UUID("7ca648c4-0507-41b0-84db-0b1a0030dba4")
    PRIVATE_KEY_PASSWORD: SecretStr = SecretStr("private-key-password")
    PRIVATE_KEY: SecretStr = SecretStr("")


@lru_cache()
def settings() -> Settings:
    return Settings()
