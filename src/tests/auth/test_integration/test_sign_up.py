import pytest
from httpx import AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.models import User
from enums import UserRolesEnum
from exceptions import CreateUserException
from services.auth import AuthService
from tests.factories.user import UserFactory
from tests.utils import get_random_str


@pytest.mark.asyncio
async def test__sign_up__success_case(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    generated_user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )
    await async_db_session.execute(delete(User).filter_by(uuid=generated_user.uuid))

    sign_up_data = {
        "username": generated_user.username,
        "password": user_raw_password,
    }

    response = await api_client.post("/api/v1/auth/sign-up", json=sign_up_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED

    user_after_sign_up = await async_db_session.scalar(select(User).filter_by(username=generated_user.username))

    assert user_after_sign_up
    assert response_data == {
        "uuid": str(user_after_sign_up.uuid),
        "username": sign_up_data.get("username"),
        "email": sign_up_data.get("email"),
        "full_name": sign_up_data.get("full_name"),
        "role": UserRolesEnum.STAFF.value,
        "is_active": True,
    }


@pytest.mark.asyncio
async def test__sign_up__user_already_exists(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    generated_user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )

    sign_up_data = {
        "username": generated_user.username,
        "password": user_raw_password,
    }

    response = await api_client.post("/api/v1/auth/sign-up", json=sign_up_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response_data.get("error") == CreateUserException.message
