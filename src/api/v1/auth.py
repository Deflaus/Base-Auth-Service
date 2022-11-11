from fastapi import APIRouter, Depends, status

from api.deps import get_access_token_payload, get_new_token_pair
from schemas.auth import SignInRequestSchema, TokenPairSchema, TokenPayload
from schemas.user import UserCreate, UserSchema
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service

router = APIRouter()


@router.post("/sign_in/", status_code=status.HTTP_201_CREATED, response_model=TokenPairSchema)
async def sign_in(
    request_data: SignInRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> TokenPairSchema:
    user = await user_service.validate_credentials(request_data.username, request_data.password)
    return await auth_service.create_pair_token(user.pk)


@router.get("/validate/", status_code=status.HTTP_200_OK, response_model=TokenPayload)
async def validate(token_payload: TokenPayload = Depends(get_access_token_payload)):
    return token_payload


@router.post("/sign_up/", status_code=status.HTTP_201_CREATED, response_model=UserSchema)
async def sign_up(
    request_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.create_user(request_data)


@router.post("/refresh/", status_code=status.HTTP_201_CREATED, response_model=TokenPairSchema)
async def refresh_token(token_pair: TokenPairSchema = Depends(get_new_token_pair)) -> TokenPairSchema:
    return token_pair
