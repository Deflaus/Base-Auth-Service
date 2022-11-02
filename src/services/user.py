from fastapi import Depends
from passlib.context import CryptContext

from db.postgres import get_postgres
from schemas.user import UserInDB


class UserService:
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, postgres: dict):
        self.postgres = postgres

    def get_user_by_username(self, username: str) -> UserInDB | None:
        user = None
        for pk, data in self.postgres.items():
            if data["username"] == username:
                user = data
                break

        if user is None:
            return None

        return UserInDB(**user)

    def get_user_by_pk(self, pk: str) -> UserInDB | None:
        user = self.postgres.get(pk, None)
        if user is None:
            return None

        return UserInDB(**user)

    @classmethod
    def verify_password(cls, raw_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(raw_password, hashed_password)


def get_user_service(postgres: dict = Depends(get_postgres)) -> UserService:
    return UserService(postgres)
