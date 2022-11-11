import uuid
from calendar import timegm
from datetime import datetime, timedelta
from functools import lru_cache

from fastapi import HTTPException, status
from jose import JWTError, jwt

from core.settings import settings
from models.redis.base import NotFoundError
from models.redis.jwt import JwtPublicKey, RefreshToken
from schemas.auth import TokenPairSchema, TokenPayload


class AuthService:
    jwt_algorithm: str = "RS256"

    @classmethod
    async def create_pair_token(cls, user_pk: uuid.UUID) -> TokenPairSchema:
        access_token_expire_delta = timedelta(minutes=settings().ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = await cls._create_token(user_pk, access_token_expire_delta)

        refresh_token_expire_delta = timedelta(days=settings().REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token = await cls._create_token(user_pk, refresh_token_expire_delta)

        await RefreshToken(pk=user_pk, token=refresh_token).save(expire_time=refresh_token_expire_delta)

        return TokenPairSchema(access=access_token, refresh=refresh_token)

    @classmethod
    async def _create_token(cls, user_pk: uuid.UUID, expires_delta: timedelta) -> str:
        expire = datetime.utcnow() + expires_delta
        token_payload = TokenPayload(user_pk=str(user_pk), exp=timegm(expire.utctimetuple())).dict()

        encoded_jwt = jwt.encode(
            token_payload,
            settings().TOKEN_PRIVATE_KEY.get_secret_value(),
            algorithm=cls.jwt_algorithm,
        )
        return encoded_jwt

    @classmethod
    async def decode_token(cls, token: str) -> TokenPayload:
        jwt_public_key: JwtPublicKey = await JwtPublicKey.get(settings().TOKEN_PUBLIC_KEY_PK)  # type: ignore
        try:
            payload = jwt.decode(token, jwt_public_key.public_key, algorithms=[cls.jwt_algorithm])
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )

        return TokenPayload.parse_obj(payload)

    @classmethod
    async def get_refresh_token_payload(cls, token: str) -> TokenPayload:
        token_payload = await cls.decode_token(token)
        try:
            token_from_cache: RefreshToken = await RefreshToken.get(uuid.UUID(token_payload.user_pk))  # type: ignore
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Token not found",
            )

        try:
            assert token_from_cache.token == token
        except AssertionError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        return token_payload

    @classmethod
    async def remove_refresh_token(cls, user_pk: uuid.UUID) -> None:
        await RefreshToken.delete(pk=user_pk)


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService()
