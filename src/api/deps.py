import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security import OAuth2

from schemas.auth import AccessTokenPayload, RefreshTokenPayload
from schemas.user import UserRolesEnum, UserSchema
from services.token import TokenService, get_token_service
from services.user import UserService, get_user_service
from utils.oauth import CookieKeyEnum


class Oauth2PasswordWithCookie(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        cookie_key: str,
        scopes: dict[str, str] | None = None,
    ):
        if not scopes:
            scopes = {}

        self._cookie_key = cookie_key

        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=None, auto_error=True)

    async def __call__(self, request: Request) -> str | None:
        access_token: str | None = request.cookies.get(self._cookie_key)
        if access_token:
            return access_token

        if not self.auto_error:
            return None

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )


oauth2_access_scheme = Oauth2PasswordWithCookie(
    tokenUrl="/api/v1/auth/sign_in", cookie_key=CookieKeyEnum.access_token.value
)
oauth2_refresh_scheme = Oauth2PasswordWithCookie(
    tokenUrl="/api/v1/auth/sign_in", cookie_key=CookieKeyEnum.refresh_token.value
)


async def get_access_token_payload(
    token: str = Depends(oauth2_access_scheme),
    token_service: TokenService = Depends(get_token_service),
) -> AccessTokenPayload:
    return await token_service.decode_access_token(token)


async def get_refresh_token_payload(
    token: str = Depends(oauth2_refresh_scheme),
    token_service: TokenService = Depends(get_token_service),
) -> RefreshTokenPayload:
    return await token_service.decode_refresh_token(token)


async def get_current_user_by_access_token(
    token_payload: AccessTokenPayload = Depends(get_access_token_payload),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.get_user_by_pk(pk=uuid.UUID(token_payload.sub))


async def get_current_user_by_refresh_token(
    token_payload: RefreshTokenPayload = Depends(get_refresh_token_payload),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.get_user_by_pk(pk=uuid.UUID(token_payload.sub))


class MinRequiredRoleChecker:
    roles_priority = {role: idx + 1 for idx, role in enumerate(UserRolesEnum)}

    def __init__(self, min_required_role: UserRolesEnum):
        self.min_required_role_priority = self.roles_priority[min_required_role]

    def __call__(self, user: UserSchema = Depends(get_current_user_by_access_token)) -> UserSchema:
        user_role_priority = self.roles_priority[user.role]
        if user_role_priority < self.min_required_role_priority:
            raise HTTPException(status_code=403, detail="Operation not permitted")

        return user
