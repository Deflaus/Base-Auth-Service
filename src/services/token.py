from calendar import timegm
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any

from fastapi import HTTPException, status
from jose import JWTError, jwt

from core.settings import settings
from models.redis.jwt import JwtPublicKey
from schemas.auth import AccessTokenPayload, RefreshTokenPayload
from schemas.user import UserSchema


class TokenService:
    jwt_algorithm: str = "RS256"

    @classmethod
    async def create_refresh_token(self, user: UserSchema) -> tuple[str, datetime]:
        refresh_token_expire_delta = timedelta(days=settings().REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + refresh_token_expire_delta
        token_payload = RefreshTokenPayload(sub=str(user.pk), exp=timegm(expire.utctimetuple()))

        return await self._create_token(token_payload), expire

    @classmethod
    async def create_access_token(cls, user: UserSchema) -> tuple[str, datetime]:
        access_token_expire_delta = timedelta(days=settings().REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + access_token_expire_delta
        token_payload = AccessTokenPayload(sub=str(user.pk), role=user.role, exp=timegm(expire.utctimetuple()))

        return await cls._create_token(token_payload), expire

    @classmethod
    async def _create_token(cls, payload: AccessTokenPayload | RefreshTokenPayload) -> str:
        encoded_jwt = jwt.encode(
            payload.dict(),
            settings().TOKEN_PRIVATE_KEY.get_secret_value(),
            algorithm=cls.jwt_algorithm,
        )
        return encoded_jwt

    @classmethod
    async def decode_access_token(cls, token: str) -> AccessTokenPayload:
        payload = await cls._decode_token(token)
        return AccessTokenPayload.parse_obj(payload)

    @classmethod
    async def decode_refresh_token(cls, token: str) -> RefreshTokenPayload:
        payload = await cls._decode_token(token)
        return RefreshTokenPayload.parse_obj(payload)

    @classmethod
    async def _decode_token(cls, token: str) -> dict[Any, Any]:
        jwt_public_key: JwtPublicKey = await JwtPublicKey.get(settings().TOKEN_PUBLIC_KEY_PK)  # type: ignore
        try:
            payload = jwt.decode(token, jwt_public_key.public_key, algorithms=[cls.jwt_algorithm])
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )

        return payload


@lru_cache
def get_token_service() -> TokenService:
    return TokenService()
