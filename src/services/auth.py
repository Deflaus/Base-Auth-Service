from datetime import datetime, timedelta

from aioredis import Redis
from fastapi import Depends
from jose import jwt
from passlib.context import CryptContext

from core.settings import settings
from db.redis import get_redis
from schemas.auth import TokenPairSchema


class AuthService:
    jwt_algorithm: str = "RS256"
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    def verify_password(cls, raw_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(raw_password, hashed_password)

    @classmethod
    def create_pair_token(cls, data: dict) -> TokenPairSchema:
        access_token_expire_delta = timedelta(minutes=settings().ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = cls._create_token(data, access_token_expire_delta)

        refresh_token_expire_delta = timedelta(days=settings().REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = cls._create_token(data, refresh_token_expire_delta)

        return TokenPairSchema(access=access_token, refresh=refresh_token)

    @classmethod
    def _create_token(cls, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        expire = datetime.now() + expires_delta
        to_encode["exp"] = datetime.strftime(expire, "%m/%d/%Y, %H:%M:%S")
        encoded_jwt = jwt.encode(
            to_encode, settings().TOKEN_PRIVATE_KEY.get_secret_value(), algorithm=cls.jwt_algorithm
        )
        return encoded_jwt


def get_auth_service(redis: Redis = Depends(get_redis)) -> AuthService:
    return AuthService(redis)
