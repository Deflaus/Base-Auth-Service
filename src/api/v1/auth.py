from fastapi import APIRouter, Depends, HTTPException, status

from schemas.auth import SignInRequestSchema, TokenPairSchema
from services.auth import AuthService, get_auth_service
from services.user import UserService, get_user_service

router = APIRouter()


@router.post("/sign_in/", response_model=TokenPairSchema)
async def sign_in(
    request_data: SignInRequestSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
) -> TokenPairSchema:
    user = user_service.get_user(username=request_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username")

    if not auth_service.verify_password(request_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    return auth_service.create_pair_token(user.pk)
