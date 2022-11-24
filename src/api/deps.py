import uuid

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from schemas.auth import TokenPairSchema, TokenPayload
from schemas.user import UserRolesEnum, UserSchema
from services.auth import TokenService, get_token_service
from services.user import UserService, get_user_service

oauth2_scheme = APIKeyHeader(name="Authorization")


async def get_token_payload(
    token: str = Depends(oauth2_scheme),
    auth_service: TokenService = Depends(get_token_service),
) -> TokenPayload:
    return await auth_service.decode_token(token)


async def get_current_user(
    token_payload: TokenPayload = Depends(get_token_payload),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.get_user_by_pk(pk=uuid.UUID(token_payload.sub))


async def get_new_token_pair(
    token_payload: TokenPayload = Depends(get_token_payload),
    auth_service: TokenService = Depends(get_token_service),
    user_service: UserService = Depends(get_user_service),
) -> TokenPairSchema:
    user = await user_service.get_user_by_pk(pk=uuid.UUID(token_payload.sub))

    return await auth_service.create_pair_token(user)


class MinRequiredRoleChecker:
    roles_priority = {role: idx + 1 for idx, role in enumerate(UserRolesEnum)}

    def __init__(self, min_required_role: UserRolesEnum):
        self.min_required_role_priority = self.roles_priority[min_required_role]

    def __call__(self, user: UserSchema = Depends(get_current_user)) -> UserSchema:
        user_role_priority = self.roles_priority[user.role]
        if user_role_priority < self.min_required_role_priority:
            raise HTTPException(status_code=403, detail="Operation not permitted")

        return user
