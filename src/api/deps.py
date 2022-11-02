from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from schemas.auth import TokenPayload
from schemas.user import UserInDB
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service

auth_key = APIKeyHeader(name="Authorization")


async def get_token_payload(
    token: str = Depends(auth_key),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPayload:
    return await auth_service.decode_token(token)


async def get_current_user(
    token: str = Depends(auth_key),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserInDB:
    token_payload = await auth_service.decode_token(token)

    user = user_service.get_user_by_pk(pk=token_payload.sub)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    return user
