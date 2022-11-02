from fastapi import APIRouter, Depends, HTTPException, status

from api.deps import get_token_payload
from schemas.auth import SignInRequestSchema, TokenPairSchema, TokenPayload
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service

router = APIRouter()


@router.post("/sign_in/", status_code=status.HTTP_201_CREATED, response_model=TokenPairSchema)
async def sign_in(
    request_data: SignInRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> TokenPairSchema:
    user = user_service.get_user_by_username(username=request_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username")

    if not user_service.verify_password(request_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    return await auth_service.create_pair_token(user.pk)


@router.get("/validate/", status_code=status.HTTP_200_OK, response_model=TokenPayload)
async def validate(token_payload: TokenPayload = Depends(get_token_payload)):
    return token_payload
