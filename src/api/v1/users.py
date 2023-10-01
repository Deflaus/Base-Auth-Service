import typing
import uuid as _uuid

from fastapi import APIRouter, Depends, Security, status

from db.models import User
from enums import UserRolesEnum
from schemas.user import UserChangeSchema, UserOutputSchema
from services.auth import get_user_by_access_token
from services.user import UserService

router = APIRouter()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[UserOutputSchema],
    dependencies=[Security(get_user_by_access_token, scopes=[UserRolesEnum.ADMIN, UserRolesEnum.SUPER_ADMIN])],
)
async def get_all_users(
    user_service: UserService = Depends(),
) -> typing.Sequence[User]:
    all_users = await user_service.get_all_users()

    return all_users


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
)
async def get_current_user(
    user: User = Depends(get_user_by_access_token),
) -> User:
    return user


@router.get(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
    dependencies=[Security(get_user_by_access_token, scopes=[UserRolesEnum.ADMIN, UserRolesEnum.SUPER_ADMIN])],
)
async def get_user_by_uuid(
    user_uuid: _uuid.UUID,
    user_service: UserService = Depends(),
) -> User:
    user = await user_service.get_user_by_uuid(user_uuid=user_uuid)

    return user


@router.patch(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
    dependencies=[Depends(get_user_by_access_token)],
)
async def change_current_user(
    user_uuid: _uuid.UUID,
    request_data: UserChangeSchema,
    user_service: UserService = Depends(),
) -> User:
    user = await user_service.change_user_by_uuid(user_uuid=user_uuid, user_data=request_data)

    return user


@router.patch(
    "/{user_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=UserOutputSchema,
    dependencies=[Security(get_user_by_access_token, scopes=[UserRolesEnum.SUPER_ADMIN])],
)
async def change_user_by_uuid(
    user_uuid: _uuid.UUID,
    request_data: UserChangeSchema,
    user_service: UserService = Depends(),
) -> User:
    user = await user_service.change_user_by_uuid(user_uuid=user_uuid, user_data=request_data)

    return user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    dependencies=[Depends(get_user_by_access_token)],
)
async def delete_current_user(
    current_user: User = Depends(get_user_by_access_token),
    user_service: UserService = Depends(),
) -> None:
    await user_service.delete_user_by_uuid(user_uuid=current_user.uuid)


@router.delete(
    "/{user_uuid}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
    dependencies=[Security(get_user_by_access_token, scopes=[UserRolesEnum.SUPER_ADMIN])],
)
async def delete_user_by_uuid(
    user_uuid: _uuid.UUID,
    user_service: UserService = Depends(),
) -> None:
    await user_service.delete_user_by_uuid(user_uuid=user_uuid)
