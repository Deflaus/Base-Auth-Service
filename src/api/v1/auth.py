import uuid

from fastapi import APIRouter, Depends, status

from api.deps import get_access_token_payload, get_new_token_pair
from core.backends import UsernameAuthBackend, get_username_auth_backend
from schemas.auth import SignInSchema, TokenPairSchema, TokenPayload
from schemas.user import UserCreate, UserSchema
from services.auth import TokenService, get_token_service
from services.user import UserService, get_user_service

router = APIRouter()


@router.post(
    "/sign_in",
    description="Login by username and password",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenPairSchema,
)
async def sign_in(
    request_data: SignInSchema,
    auth_backend: UsernameAuthBackend = Depends(get_username_auth_backend),
    auth_service: TokenService = Depends(get_token_service),
) -> TokenPairSchema:
    user = await auth_backend.authenticate(request_data.username, request_data.password)
    return await auth_service.create_pair_token(user)


@router.get(
    "/validate",
    description="Get token payload",
    status_code=status.HTTP_200_OK,
    response_model=TokenPayload,
)
async def validate(token_payload: TokenPayload = Depends(get_access_token_payload)):
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
    "/refresh",
    description="Refresh token pair by refresh token in Authorization header",
    status_code=status.HTTP_201_CREATED,
    response_model=TokenPairSchema,
)
async def refresh_token(token_pair: TokenPairSchema = Depends(get_new_token_pair)) -> TokenPairSchema:
    return token_pair


@router.post(
    "/logout",
    description="Delete refresh token",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    token_payload: TokenPayload = Depends(get_access_token_payload),
    auth_service: TokenService = Depends(get_token_service),
) -> None:
    await auth_service.remove_refresh_token(uuid.UUID(token_payload.sub))
