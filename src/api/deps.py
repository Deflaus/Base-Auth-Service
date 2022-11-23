import uuid

from fastapi import Depends
from fastapi.security import APIKeyHeader

from schemas.auth import TokenPairSchema, TokenPayload
from schemas.user import UserSchema
from services.auth import TokenService, get_token_service
from services.user import UserService, get_user_service

oauth2_scheme = APIKeyHeader(name="Authorization")


async def get_access_token_payload(
    token: str = Depends(oauth2_scheme),
    auth_service: TokenService = Depends(get_token_service),
) -> TokenPayload:
    return await auth_service.decode_token(token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
    auth_service: TokenService = Depends(get_token_service),
) -> UserSchema:
    token_payload = await auth_service.decode_token(token)
    user = await user_service.get_user_by_pk(pk=uuid.UUID(token_payload.sub))

    return user


async def get_new_token_pair(
    token: str = Depends(oauth2_scheme),
    auth_service: TokenService = Depends(get_token_service),
    user_service: UserService = Depends(get_user_service),
) -> TokenPairSchema:
    token_payload = await auth_service.get_refresh_token_payload(token)
    user = await user_service.get_user_by_pk(pk=uuid.UUID(token_payload.sub))

    return await auth_service.create_pair_token(user)
