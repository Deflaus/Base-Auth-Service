import calendar
import datetime as dt
import typing
import uuid as _uuid

from fastapi import Depends
from fastapi.security import SecurityScopes
from jose import ExpiredSignatureError, JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.postgres import get_session
from db.repositories.jwt import JwtPublicKeyRepository
from db.repositories.jwt_session import JwtSessionRepository
from db.repositories.user import UserRepository
from enums import HeaderKeyEnum, UserRolesEnum
from exceptions import (
    InvalidPasswordException,
    OperationNotPermittedException,
    TokenDecodeException,
    TokenIsExpiredException,
    UserNotFoundException,
)
from schemas.auth import (
    AccessTokenOutputSchema,
    AccessTokenPayloadSchema,
    RefreshTokenPayloadSchema,
    SignInInputSchema,
    SignUpInputSchema,
    TokenPairOutputSchema,
)
from schemas.jwt import JwtPublicKeySchema
from schemas.jwt_session import JwtSessionCreateSchema
from schemas.user import UserCreateSchema
from settings import Settings, get_settings
from utils.headers import APIKeyHeader

access_token_scheme = APIKeyHeader(name=HeaderKeyEnum.ACCESS_TOKEN, scheme_name=HeaderKeyEnum.ACCESS_TOKEN)
refresh_token_scheme = APIKeyHeader(name=HeaderKeyEnum.REFRESH_TOKEN, scheme_name=HeaderKeyEnum.REFRESH_TOKEN)


class AuthService:
    _jwt_algorithm: str = "RS256"
    _password_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        session: AsyncSession = Depends(get_session),
        user_repository: UserRepository = Depends(),
        jwt_session_repository: JwtSessionRepository = Depends(),
        jwt_public_key_repository: JwtPublicKeyRepository = Depends(),
    ) -> None:
        self._settings = settings

        self._session = session
        self._user_repository = user_repository
        self._jwt_session_repository = jwt_session_repository
        self._jwt_public_key_repository = jwt_public_key_repository

    async def authenticate_user_and_create_token_pair(
        self,
        credentials: SignInInputSchema,
    ) -> TokenPairOutputSchema:
        user = await self._user_repository.get_active_user_by_username(username=credentials.username)
        if not user:
            logger.error(f"User with username {credentials.username} not found")
            raise UserNotFoundException

        is_passwords_equal = self._password_context.verify(credentials.password, user.password)
        if is_passwords_equal is False:
            logger.error(f"Invalid password {credentials.password} for user {user.username}")
            raise InvalidPasswordException

        refresh_token_expire_delta = dt.timedelta(days=self._settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) + refresh_token_expire_delta
        refresh_token = self._create_refresh_token(user, expires_at=refresh_token_expires_at)

        access_token_expire_delta = dt.timedelta(minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) + access_token_expire_delta
        access_token = self._create_access_token(user, expires_at=access_token_expires_at)

        jwt_session_data = JwtSessionCreateSchema(
            user_uuid=user.uuid, refresh_token=refresh_token, expires_at=refresh_token_expires_at
        )
        await self._jwt_session_repository.create_jwt_session(data=jwt_session_data)

        await self._session.commit()

        return TokenPairOutputSchema(
            refresh_token=refresh_token,
            access_token=access_token,
        )

    def create_access_token(self, user: User) -> AccessTokenOutputSchema:
        access_token_expire_delta = dt.timedelta(minutes=self._settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) + access_token_expire_delta
        access_token = self._create_access_token(user, expires_at=access_token_expires_at)

        return AccessTokenOutputSchema(access_token=access_token)

    def _create_refresh_token(self, user: User, expires_at: dt.datetime) -> str:
        token_payload = RefreshTokenPayloadSchema(
            sub=str(user.uuid),
            exp=calendar.timegm(expires_at.utctimetuple()),
        )

        return self._create_token(token_payload)

    def _create_access_token(self, user: User, expires_at: dt.datetime) -> str:
        token_payload = AccessTokenPayloadSchema(
            sub=str(user.uuid),
            exp=calendar.timegm(expires_at.utctimetuple()),
        )

        return self._create_token(token_payload)

    def _create_token(self, payload: AccessTokenPayloadSchema | RefreshTokenPayloadSchema) -> str:
        encoded_jwt = jwt.encode(
            claims=payload.model_dump(),
            key=self._settings.TOKEN_PRIVATE_KEY,
            algorithm=self._jwt_algorithm,
        )

        return encoded_jwt

    async def decode_access_token(self, token: str) -> AccessTokenPayloadSchema:
        payload = await self._decode_token(token)
        return AccessTokenPayloadSchema.model_validate(payload)

    async def decode_refresh_token(self, token: str) -> RefreshTokenPayloadSchema:
        payload = await self._decode_token(token)
        return RefreshTokenPayloadSchema.model_validate(payload)

    async def _decode_token(self, token: str) -> dict[str, typing.Any]:
        public_key_data: JwtPublicKeySchema = await self._jwt_public_key_repository.get(  # type: ignore
            pk=self._settings.TOKEN_PUBLIC_KEY_PK,
        )

        try:
            payload = jwt.decode(token, public_key_data.public_key, algorithms=[self._jwt_algorithm])

        except ExpiredSignatureError:
            logger.error("Token is expired")
            raise TokenIsExpiredException

        except JWTError as e:
            logger.error(f"Decode token error: {e}")
            raise TokenDecodeException(error=e)

        return payload

    async def get_active_user_with_not_denied_sessions_by_uuid(self, user_uuid: _uuid.UUID) -> User:
        user = await self._user_repository.get_active_user_with_not_denied_sessions_by_uuid(uuid=user_uuid)
        if not user:
            raise UserNotFoundException

        return user

    async def sign_up(self, credentials: SignUpInputSchema) -> User:
        hashed_password = self.hash_password(credentials.password)

        user_data = UserCreateSchema(
            username=credentials.username,
            password=hashed_password,
            full_name=credentials.full_name,
            email=credentials.email,
            is_active=True,
            role=UserRolesEnum.STAFF,
        )
        user = await self._user_repository.create_user(data=user_data)

        await self._session.commit()

        return user

    @classmethod
    def hash_password(cls, raw_password: str) -> str:
        return cls._password_context.hash(raw_password)

    async def delete_user_session(self, user: User) -> None:
        await self._jwt_session_repository.delete_jwt_session_by_user_uuid(user_uuid=user.uuid)
        await self._session.commit()


def _has_permissions(security_scopes: SecurityScopes, user: User) -> None:
    if security_scopes.scopes and user.role not in security_scopes.scopes:
        raise OperationNotPermittedException


async def get_user_by_access_token(
    security_scopes: SecurityScopes,
    access_token: str = Depends(access_token_scheme),
    auth_service: AuthService = Depends(),
) -> User:
    token_payload = await auth_service.decode_access_token(token=access_token)
    user = await auth_service.get_active_user_with_not_denied_sessions_by_uuid(user_uuid=_uuid.UUID(token_payload.sub))
    _has_permissions(security_scopes, user)
    return user


async def get_user_by_refresh_token(
    security_scopes: SecurityScopes,
    refresh_token: str = Depends(refresh_token_scheme),
    auth_service: AuthService = Depends(),
) -> User:
    token_payload = await auth_service.decode_refresh_token(token=refresh_token)
    user = await auth_service.get_active_user_with_not_denied_sessions_by_uuid(user_uuid=_uuid.UUID(token_payload.sub))
    _has_permissions(security_scopes, user)
    return user
