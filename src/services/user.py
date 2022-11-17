import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres
from models.postgres import User
from schemas.user import UserCreate, UserSchema, UserUpdate


class UserService:
    def __init__(self, postgres: AsyncSession):
        self.postgres = postgres

    async def get_user_by_pk(self, pk: uuid.UUID) -> UserSchema:
        user = await User.get(session=self.postgres, pk=pk)
        return UserSchema.from_orm(user)

    async def create_user(self, data: UserCreate) -> UserSchema:
        new_user = await User(**data.dict()).save(self.postgres)
        return UserSchema.from_orm(new_user)

    async def update_user(self, pk: uuid.UUID, data: UserUpdate) -> UserSchema:
        user = await User.get(pk=pk, session=self.postgres)
        await user.update(values_to_update=data.dict(), session=self.postgres)
        return UserSchema.from_orm(user)

    async def delete_user(self, pk: uuid.UUID) -> None:
        await User.delete(pk=pk, session=self.postgres)


@lru_cache
def get_user_service(postgres: AsyncSession = Depends(get_postgres)) -> UserService:
    return UserService(postgres)
