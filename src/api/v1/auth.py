from fastapi import APIRouter, Depends, Response, status

from api.deps import (
    get_access_token_payload,
    get_current_user_by_refresh_token,
    get_refresh_token_payload,
)
from core.backends import UsernameAuthBackend, get_username_auth_backend
from schemas.auth import AccessTokenPayload, RefreshTokenPayload
from schemas.jwt import JwtSessionCreate
from schemas.user import UserCreate, UserSchema
from services.jwt_session import JwtSessionService, get_jwt_session_service
from services.token import TokenService, get_token_service
from services.user import UserService, get_user_service
from utils.oauth import CookieKeyEnum, OAuth2PasswordRequestForm

router = APIRouter()


@router.post(
    "/sign_in",
    description="Create refresh token by username and password",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
async def sign_in(
    response: Response,
    request_data: OAuth2PasswordRequestForm = Depends(),
    auth_backend: UsernameAuthBackend = Depends(get_username_auth_backend),
    token_service: TokenService = Depends(get_token_service),
    jwt_session_service: JwtSessionService = Depends(get_jwt_session_service),
) -> None:
    user = await auth_backend.authenticate(request_data.username, request_data.password)
    refresh_token, expires_at = await token_service.create_refresh_token(user)

    jwt_session_data = JwtSessionCreate(refresh_token=refresh_token, user_pk=user.pk, expires_at=expires_at)
    await jwt_session_service.create_session(jwt_session_data)

    response.set_cookie(key=CookieKeyEnum.refresh_token.value, value=refresh_token, httponly=True)


@router.post(
    "/access",
    description="Create access token",
    status_code=status.HTTP_201_CREATED,
    response_model=None,
)
async def create_access_token(
    response: Response,
    user: UserSchema = Depends(get_current_user_by_refresh_token),
    token_service: TokenService = Depends(get_token_service),
) -> None:
    access_token, _ = await token_service.create_access_token(user)

    response.set_cookie(key=CookieKeyEnum.access_token.value, value=access_token, httponly=True)


@router.get(
    "/validate_access",
    description="Get access token payload",
    status_code=status.HTTP_200_OK,
    response_model=AccessTokenPayload,
)
async def validate_access_token(token_payload: AccessTokenPayload = Depends(get_access_token_payload)):
    return token_payload


@router.get(
    "/validate_refresh",
    description="Get refresh token payload",
    status_code=status.HTTP_200_OK,
    response_model=RefreshTokenPayload,
)
async def validate_refresh_token(token_payload: RefreshTokenPayload = Depends(get_refresh_token_payload)):
    return token_payload


@router.post(
    "/sign_up",
    description="Create new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserSchema,
)
async def sign_up(
    request_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.create_user(request_data)


@router.post(
    "/sign_out",
    description="Deny jwt session and remove tokens from cookies",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def sign_out(
    response: Response,
    user: UserSchema = Depends(get_current_user_by_refresh_token),
    jwt_session_service: JwtSessionService = Depends(get_jwt_session_service),
) -> None:
    await jwt_session_service.deny_session(user_pk=user.pk)

    response.delete_cookie(key=CookieKeyEnum.access_token.value, httponly=True)
    response.delete_cookie(key=CookieKeyEnum.refresh_token.value, httponly=True)
