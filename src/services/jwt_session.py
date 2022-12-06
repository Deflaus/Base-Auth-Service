import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_postgres
from models.postgres import JwtSession
from schemas.jwt import JwtSessionCreate, JwtSessionGet


class JwtSessionService:
    def __init__(self, postgres: AsyncSession):
        self.postgres = postgres

    async def get_session_by_user_pk(self, user_pk: uuid.UUID) -> JwtSessionGet:
        jwt_session = await JwtSession.get(session=self.postgres, user_pk=user_pk)
        return JwtSessionGet.from_orm(jwt_session)

    async def create_session(self, data: JwtSessionCreate) -> JwtSessionGet:
        new_jwt_session = await JwtSession(**data.dict()).save(self.postgres)
        return JwtSessionGet.from_orm(new_jwt_session)

    async def deny_session(self, user_pk: uuid.UUID) -> None:
        jwt_session = await JwtSession.get(session=self.postgres, user_pk=user_pk)
        await jwt_session.update(values_to_update={"is_denied": True}, session=self.postgres)


@lru_cache
def get_jwt_session_service(postgres: AsyncSession = Depends(get_postgres)) -> JwtSessionService:
    return JwtSessionService(postgres)
