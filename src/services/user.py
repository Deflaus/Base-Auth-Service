from functools import lru_cache
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres
from models.postgres import User
from schemas.user import UserCreate, UserSchema


class UserService:
    def __init__(self, postgres: AsyncSession):
        self.postgres = postgres

    async def validate_credentials(self, username: str, password: str) -> UserSchema:
        user: User | None = (
            (await self.postgres.execute(select(User).where(User.username == username))).scalars().first()
        )
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")

        if not user.verify_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        return UserSchema.from_orm(user)

    async def get_user_by_pk(self, pk: UUID) -> UserSchema:
        user = await User.get(pk=pk, session=self.postgres)
        return UserSchema.from_orm(user)

    async def create_user(self, data: UserCreate) -> UserSchema:
        new_user = await User(**data.dict()).save(self.postgres)
        return UserSchema.from_orm(new_user)


@lru_cache
def get_user_service(postgres: AsyncSession = Depends(get_postgres)) -> UserService:
    return UserService(postgres)
