import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from db.models import JwtSession
from exceptions import InvalidPasswordException, UserNotFoundException
from services.auth import AuthService
from tests.factories.user import UserFactory
from tests.utils import get_random_str


@pytest.mark.asyncio
async def test__sign_in__success_case(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )
    sign_in_data = {
        "username": user.username,
        "password": user_raw_password,
    }

    response = await api_client.post("/api/v1/auth/sign-in", json=sign_in_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data.pop("access_token", None)
    assert response_data.pop("refresh_token", None)
    assert not response_data

    jwt_session_after_sign_in = (
        await async_db_session.execute(select(JwtSession).filter_by(user_uuid=user.uuid))
    ).scalar_one_or_none()

    assert jwt_session_after_sign_in


@pytest.mark.asyncio
async def test__sign_in__inactive_user(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=False,
    )
    sign_in_data = {
        "username": user.username,
        "password": user_raw_password,
    }

    response = await api_client.post("/api/v1/auth/sign-in", json=sign_in_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data.get("error") == UserNotFoundException.message

    jwt_session_after_sign_in = await async_db_session.scalar(select(JwtSession).filter_by(user_uuid=user.uuid))
    assert jwt_session_after_sign_in is None


@pytest.mark.asyncio
async def test__sign_in__not_exists_user(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    sign_in_data = {
        "username": get_random_str(),
        "password": get_random_str(),
    }

    response = await api_client.post("/api/v1/auth/sign-in", json=sign_in_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data.get("error") == UserNotFoundException.message

    jwt_sessions_after_sign_in = (await async_db_session.scalars(select(JwtSession))).all()
    assert not jwt_sessions_after_sign_in


@pytest.mark.asyncio
async def test__sign_in__invalid_password(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(get_random_str()),
        is_active=True,
    )
    sign_in_data = {
        "username": user.username,
        "password": get_random_str(),
    }

    response = await api_client.post("/api/v1/auth/sign-in", json=sign_in_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response_data.get("error") == InvalidPasswordException.message

    jwt_session_after_sign_in = await async_db_session.scalar(select(JwtSession).filter_by(user_uuid=user.uuid))
    assert not jwt_session_after_sign_in
