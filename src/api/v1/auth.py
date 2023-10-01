from fastapi import APIRouter, Depends, status

from db.models import User
from schemas.auth import (
    AccessTokenOutputSchema,
    AccessTokenPayloadSchema,
    RefreshTokenPayloadSchema,
    SignInInputSchema,
    SignUpInputSchema,
    TokenPairOutputSchema,
)
from schemas.user import UserOutputSchema
from services.auth import (
    AuthService,
    access_token_scheme,
    get_user_by_refresh_token,
    refresh_token_scheme,
)

router = APIRouter()


@router.post(
    "/sign-in",
    description="Create token pair by username and password",
    status_code=status.HTTP_201_CREATED,
)
async def sign_in(
    request_data: SignInInputSchema,
    auth_service: AuthService = Depends(),
) -> TokenPairOutputSchema:
    token_pair = await auth_service.authenticate_user_and_create_token_pair(credentials=request_data)

    return token_pair


@router.post(
    "/access",
    status_code=status.HTTP_201_CREATED,
)
def recreate_access_token(
    user: User = Depends(get_user_by_refresh_token),
    auth_service: AuthService = Depends(),
) -> AccessTokenOutputSchema:
    access_token = auth_service.create_access_token(user=user)

    return access_token


@router.get(
    "/validate-access",
    description="Get access token payload",
    status_code=status.HTTP_200_OK,
)
async def validate_access_token(
    access_token: str = Depends(access_token_scheme),
    auth_service: AuthService = Depends(),
) -> AccessTokenPayloadSchema:
    return await auth_service.decode_access_token(token=access_token)


@router.get(
    "/validate-refresh",
    description="Get refresh token payload",
    status_code=status.HTTP_200_OK,
)
async def validate_refresh_token(
    refresh_token: str = Depends(refresh_token_scheme),
    auth_service: AuthService = Depends(),
) -> RefreshTokenPayloadSchema:
    return await auth_service.decode_refresh_token(token=refresh_token)


@router.post(
    "/sign-up",
    description="Create new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOutputSchema,
)
async def sign_up(
    request_data: SignUpInputSchema,
    auth_service: AuthService = Depends(),
) -> User:
    user = await auth_service.sign_up(credentials=request_data)

    return user


@router.post(
    "/sign-out",
    description="Delete jwt session",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def sign_out(
    user: User = Depends(get_user_by_refresh_token),
    auth_service: AuthService = Depends(),
) -> None:
    await auth_service.delete_user_session(user=user)
