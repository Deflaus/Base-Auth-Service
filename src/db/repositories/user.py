import typing
import uuid as _uuid

from loguru import logger
from sqlalchemy import and_, delete, insert, select, update
from sqlalchemy.exc import DBAPIError

from db.models import JwtSession, User
from db.repositories.base import BaseDatabaseRepository
from exceptions import CreateUserException
from schemas.user import UserChangeSchema, UserCreateSchema


class UserRepository(BaseDatabaseRepository):
    async def get_active_user_by_username(self, username: str) -> User | None:
        stmt = select(User).filter_by(username=username, is_active=True)

        user = await self._session.scalar(stmt)

        return user

    async def get_active_user_with_not_denied_sessions_by_uuid(self, uuid: _uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .filter_by(uuid=uuid, is_active=True)
            .join(
                JwtSession,
                and_(
                    User.uuid == JwtSession.user_uuid,
                    JwtSession.is_denied == False,  # noqa: E712
                ),
            )
        )

        user = await self._session.scalar(stmt)

        return user

    async def create_user(self, data: UserCreateSchema) -> User:
        stmt = insert(User).values(data.model_dump(exclude_unset=True)).returning(User)

        try:
            user = (await self._session.execute(stmt)).scalar_one()

        except DBAPIError as e:
            logger.exception(f"Create user exception: {e}")
            raise CreateUserException

        await self._session.flush()

        return user

    async def get_all_users(self) -> typing.Sequence[User]:
        stmt = select(User).order_by(User.uuid)

        all_users = (await self._session.scalars(stmt)).all()

        return all_users

    async def get_user_by_uuid(self, user_uuid: _uuid.UUID) -> User | None:
        stmt = select(User).filter_by(uuid=user_uuid)

        user = await self._session.scalar(stmt)

        return user

    async def change_user_by_uuid(
        self,
        user_uuid: _uuid.UUID,
        user_data: UserChangeSchema,
    ) -> User | None:
        stmt = update(User).filter_by(uuid=user_uuid).values(user_data.model_dump(exclude_unset=True)).returning(User)

        changed_user = await self._session.scalar(stmt)
        await self._session.flush()

        return changed_user

    async def delete_user_by_uuid(self, user_uuid: _uuid.UUID) -> User | None:
        stmt = delete(User).filter_by(uuid=user_uuid).returning(User)

        deleted_user = await self._session.scalar(stmt)
        await self._session.flush()

        return deleted_user
