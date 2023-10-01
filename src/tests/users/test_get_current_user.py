import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from enums import HeaderKeyEnum, UserRolesEnum
from exceptions import HeaderIsNotProvidedException
from schemas.user import UserOutputSchema
from services.auth import AuthService
from tests.factories.jwt_session import JwtSessionFactory
from tests.factories.user import UserFactory
from tests.utils import get_access_token, get_random_str, get_refresh_token


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "requested_user_role",
    [
        pytest.param(UserRolesEnum.SUPER_ADMIN, id="admin"),
        pytest.param(UserRolesEnum.ADMIN, id="super_admin"),
        pytest.param(UserRolesEnum.STAFF, id="staff"),
    ],
)
async def test__get_current_user__success_case(
    requested_user_role: UserRolesEnum,
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    user = await UserFactory.create(
        session=async_db_session,
        role=requested_user_role,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid)
    user_access_token, _ = get_access_token(user_uuid=user.uuid)

    await JwtSessionFactory.create(
        session=async_db_session,
        user_uuid=user.uuid,
        refresh_token=user_refresh_token,
        is_denied=False,
    )

    headers = {
        HeaderKeyEnum.ACCESS_TOKEN.value: user_access_token,
    }

    response = await api_client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == UserOutputSchema.model_validate(user).model_dump(mode="json")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "requested_user_role",
    [
        pytest.param(UserRolesEnum.SUPER_ADMIN, id="admin"),
        pytest.param(UserRolesEnum.ADMIN, id="super_admin"),
        pytest.param(UserRolesEnum.STAFF, id="staff"),
    ],
)
async def test__get_current_user__without_access_token(
    requested_user_role: UserRolesEnum,
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user = await UserFactory.create(
        session=async_db_session,
        role=requested_user_role,
        password=AuthService.hash_password(get_random_str()),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid)
    user_access_token, _ = get_access_token(user_uuid=user.uuid)

    await JwtSessionFactory.create(
        session=async_db_session,
        user_uuid=user.uuid,
        refresh_token=user_refresh_token,
        is_denied=False,
    )

    response = await api_client.get("/api/v1/users/me")
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == HeaderIsNotProvidedException(header=HeaderKeyEnum.ACCESS_TOKEN.value).message
