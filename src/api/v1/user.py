from fastapi import APIRouter, Depends, status

from api.deps import get_current_user
from schemas.user import UserSchema, UserUpdate
from services.user import UserService, get_user_service

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserSchema)
async def get_user(
    user: UserSchema = Depends(get_current_user),
):
    return user


@router.patch("/", status_code=status.HTTP_200_OK, response_model=UserSchema)
async def update_user(
    request_data: UserUpdate,
    user: UserSchema = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> UserSchema:
    return await user_service.update_user(pk=user.pk, data=request_data)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_user(
    user: UserSchema = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
) -> None:
    return await user_service.delete_user(pk=user.pk)
