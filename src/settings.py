import pathlib
import uuid
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).resolve().parent

    ENVIRONMENT: str = "local"
    CORS_ALLOW_ORIGINS: str = "http://localhost:8000"
    cors_allow_origin_list: list[str] = CORS_ALLOW_ORIGINS.split("&")

    REDIS_DSN: str = "redis://localhost:6379/"

    TOKEN_PUBLIC_KEY_PK: uuid.UUID = uuid.UUID("7ca648c4-0507-41b0-84db-0b1a0030dba4")

    TOKEN_PRIVATE_KEY_PASSWORD: str = "CHANGE_ME"
    TOKEN_PRIVATE_KEY: str = ""

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    POSTGRES_HOST: str = "0.0.0.0"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "auth-service"
    POSTGRES_PASSWORD: str = "auth-service"
    POSTGRES_DB: str = "auth-service"

    @property
    def postgres_dsn(self):
        database = self.POSTGRES_DB if self.ENVIRONMENT != "test" else f"{self.POSTGRES_DB}_test"
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{database}"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
