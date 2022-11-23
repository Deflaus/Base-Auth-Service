from functools import lru_cache

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres
from models.postgres import User
from schemas.user import UserSchema


class UsernameAuthBackend:
    def __init__(self, postgres: AsyncSession):
        self.postgres = postgres

    async def authenticate(self, username: str, password: str) -> UserSchema:
        if username is None or password is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        user = await User.get(session=self.postgres, username=username)
        if not user.verify_password(password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

        return UserSchema.from_orm(user)


@lru_cache
def get_username_auth_backend(postgres: AsyncSession = Depends(get_postgres)) -> UsernameAuthBackend:
    return UsernameAuthBackend(postgres)
