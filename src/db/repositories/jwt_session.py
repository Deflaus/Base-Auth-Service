import uuid as _uuid

from sqlalchemy import delete, insert

from db.models import JwtSession
from db.repositories.base import BaseDatabaseRepository
from schemas.jwt_session import JwtSessionCreateSchema


class JwtSessionRepository(BaseDatabaseRepository):
    async def create_jwt_session(self, data: JwtSessionCreateSchema) -> JwtSession:
        stmt = insert(JwtSession).values(**data.model_dump()).returning(JwtSession)

        jwt_session = (await self._session.execute(stmt)).scalar_one()
        await self._session.flush()

        return jwt_session

    async def delete_jwt_session_by_user_uuid(self, user_uuid: _uuid.UUID) -> None:
        stmt = delete(JwtSession).filter_by(user_uuid=user_uuid)

        await self._session.execute(stmt)
        await self._session.flush()
