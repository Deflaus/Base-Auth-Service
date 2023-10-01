import typing
import uuid as _uuid

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
from db.postgres import get_session
from db.repositories.user import UserRepository
from exceptions import UserNotFoundException
from schemas.user import UserChangeSchema
from settings import Settings, get_settings


class UserService:
    def __init__(
        self,
        settings: Settings = Depends(get_settings),
        session: AsyncSession = Depends(get_session),
        user_repository: UserRepository = Depends(),
    ) -> None:
        self._settings = settings

        self._session = session
        self._user_repository = user_repository

    async def get_all_users(self) -> typing.Sequence[User]:
        all_users = await self._user_repository.get_all_users()

        return all_users

    async def get_user_by_uuid(self, user_uuid: _uuid.UUID) -> User:
        user = await self._user_repository.get_user_by_uuid(user_uuid)
        if user is None:
            logger.error(f"User with uuid {user_uuid} not found")
            raise UserNotFoundException

        return user

    async def change_user_by_uuid(
        self,
        user_uuid: _uuid.UUID,
        user_data: UserChangeSchema,
    ) -> User:
        changed_user = await self._user_repository.change_user_by_uuid(user_uuid, user_data=user_data)
        if changed_user is None:
            logger.error(f"User with uuid {user_uuid} not found")
            raise UserNotFoundException

        await self._session.commit()

        return changed_user

    async def delete_user_by_uuid(self, user_uuid: _uuid.UUID) -> None:
        deleted_user = await self._user_repository.delete_user_by_uuid(user_uuid)
        if deleted_user is None:
            logger.error(f"User with uuid {user_uuid} not found")
            raise UserNotFoundException

        await self._session.commit()
