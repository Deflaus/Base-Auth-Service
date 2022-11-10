from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from schemas.auth import TokenPayload
from schemas.user import UserSchema
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service

oauth2_scheme = APIKeyHeader(name="Authorization")


async def get_token_payload(
    token: str = Depends(oauth2_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPayload:
    return await auth_service.decode_token(token)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserSchema:
    token_payload = await auth_service.decode_token(token)

    user = await user_service.get_user_by_pk(pk=UUID(token_payload.user_pk))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    return user
