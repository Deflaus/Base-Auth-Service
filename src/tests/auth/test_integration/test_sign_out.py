import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from enums import HeaderKeyEnum
from exceptions import (
    HeaderIsNotProvidedException,
    TokenDecodeException,
    TokenIsExpiredException,
    UserNotFoundException,
)
from services.auth import AuthService
from tests.factories.jwt_session import JwtSessionFactory
from tests.factories.user import UserFactory
from tests.utils import get_random_str, get_refresh_token


@pytest.mark.asyncio
async def test__sign_out__success_case(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid)

    await JwtSessionFactory.create(
        session=async_db_session,
        user_uuid=user.uuid,
        refresh_token=user_refresh_token,
        is_denied=False,
    )

    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: user_refresh_token,
    }

    response = await api_client.post("/api/v1/auth/sign-out", headers=recreate_access_token_headers)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test__sign_out__jwt_session_is_denied(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid)

    await JwtSessionFactory.create(
        session=async_db_session,
        user_uuid=user.uuid,
        refresh_token=user_refresh_token,
        is_denied=True,
    )

    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: user_refresh_token,
    }

    response = await api_client.post("/api/v1/auth/sign-out", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data.get("error") == UserNotFoundException.message


@pytest.mark.asyncio
async def test__sign_out__not_exists_jwt_session(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user_raw_password = get_random_str()

    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(user_raw_password),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid)

    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: user_refresh_token,
    }

    response = await api_client.post("/api/v1/auth/sign-out", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response_data.get("error") == UserNotFoundException.message


@pytest.mark.asyncio
async def test__sign_out__expired_refresh_token(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(get_random_str()),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid, is_expired=True)

    await JwtSessionFactory.create(
        session=async_db_session,
        user_uuid=user.uuid,
        refresh_token=user_refresh_token,
        is_denied=False,
    )

    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: user_refresh_token,
    }

    response = await api_client.post("/api/v1/auth/sign-out", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == TokenIsExpiredException.message


@pytest.mark.asyncio
async def test__sign_out__without_refresh_token(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    response = await api_client.post("/api/v1/auth/sign-out")
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == HeaderIsNotProvidedException(header=HeaderKeyEnum.REFRESH_TOKEN.value).message


@pytest.mark.asyncio
async def test__sign_out__invalid_refresh_token(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: get_random_str(),
    }

    response = await api_client.post("/api/v1/auth/sign-out", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == TokenDecodeException(error="Not enough segments").message
