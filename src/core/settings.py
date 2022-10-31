import uuid
from functools import lru_cache

from pydantic import BaseSettings, RedisDsn, SecretStr


class Settings(BaseSettings):
    ENVIRONMENT: str = "local"
    REDIS_DSN: RedisDsn | str = "redis://0.0.0.0:6379/"
    TOKEN_PUBLIC_KEY_PK: uuid.UUID = uuid.UUID("7ca648c4-0507-41b0-84db-0b1a0030dba4")
    TOKEN_PRIVATE_KEY_PASSWORD: SecretStr = SecretStr("private-key-password")
    TOKEN_PRIVATE_KEY: SecretStr = SecretStr("")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30


@lru_cache()
def settings() -> Settings:
    return Settings()
