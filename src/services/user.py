from fastapi import Depends

from db.postgres import get_postgres
from schemas.user import UserInDB


class UserService:
    def __init__(self, postgres: dict):
        self.postgres = postgres

    def get_user(self, username: str) -> UserInDB | None:
        user = self.postgres.get(username, None)
        if user is None:
            return None

        return UserInDB(**user)


def get_user_service(postgres: dict = Depends(get_postgres)) -> UserService:
    return UserService(postgres)
