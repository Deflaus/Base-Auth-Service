import calendar

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from enums import HeaderKeyEnum
from exceptions import (
    HeaderIsNotProvidedException,
    TokenDecodeException,
    TokenIsExpiredException,
)
from services.auth import AuthService
from tests.factories.user import UserFactory
from tests.utils import get_random_str, get_refresh_token


@pytest.mark.asyncio
async def test__validate_refresh_token__success_case(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(get_random_str()),
        is_active=True,
    )
    user_refresh_token, refresh_token_expires_at = get_refresh_token(user_uuid=user.uuid)

    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: user_refresh_token,
    }

    response = await api_client.get("/api/v1/auth/validate-refresh", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data.pop("sub") == str(user.uuid)
    assert response_data.pop("exp") == calendar.timegm(refresh_token_expires_at.utctimetuple())
    assert not response_data


@pytest.mark.asyncio
async def test__validate_refresh_token__expired_refresh_token(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    user = await UserFactory.create(
        session=async_db_session,
        password=AuthService.hash_password(get_random_str()),
        is_active=True,
    )
    user_refresh_token, _ = get_refresh_token(user_uuid=user.uuid, is_expired=True)

    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: user_refresh_token,
    }

    response = await api_client.get("/api/v1/auth/validate-refresh", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == TokenIsExpiredException.message


@pytest.mark.asyncio
async def test__validate_refresh_token__invalid_refresh_token(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    recreate_access_token_headers = {
        HeaderKeyEnum.REFRESH_TOKEN.value: get_random_str(),
    }

    response = await api_client.get("/api/v1/auth/validate-refresh", headers=recreate_access_token_headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == TokenDecodeException(error="Not enough segments").message


@pytest.mark.asyncio
async def test__validate_refresh_token__without_refresh_token(
    async_db_session: AsyncSession,
    api_client: AsyncClient,
) -> None:
    response = await api_client.get("/api/v1/auth/validate-refresh")
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_data.get("error") == HeaderIsNotProvidedException(header=HeaderKeyEnum.REFRESH_TOKEN.value).message
