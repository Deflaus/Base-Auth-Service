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


class TokenService:
    jwt_algorithm: str = "RS256"

    @classmethod
    async def create_pair_token(cls, user_pk: uuid.UUID) -> TokenPairSchema:
        await cls._check_possibility_to_perform_login_or_refresh_operation(user_pk=user_pk)

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

        await cls._check_timeout_refresh_operation(token_from_cache.created_at)
        if token_from_cache.token != token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token",
            )

        return token_payload

    @staticmethod
    async def remove_refresh_token(user_pk: uuid.UUID) -> None:
        await RefreshToken.delete(pk=user_pk)

    @classmethod
    async def _check_possibility_to_perform_login_or_refresh_operation(cls, user_pk: uuid.UUID) -> None:
        try:
            refresh_token: RefreshToken = await RefreshToken.get(pk=user_pk)  # type: ignore
        except NotFoundError:
            return

        await cls._check_timeout_refresh_operation(refresh_token.created_at)

    @staticmethod
    async def _check_timeout_refresh_operation(last_refresh_time: int) -> None:
        if (timegm(datetime.now().utctimetuple()) - last_refresh_time) > 60:
            return

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need to wait 60 seconds before the next login or refresh operation",
        )


@lru_cache
def get_token_service() -> TokenService:
    return TokenService()
