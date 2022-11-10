from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

BaseClass = declarative_base()


class BaseModel(BaseClass):  # type: ignore
    __abstract__ = True

    @classmethod
    def verbose_name(cls) -> str:
        return cls.__tablename__

    @classmethod
    async def get_list(cls, offset: int | None, limit: int | None, session: AsyncSession) -> list["BaseModel"]:
        query = select(cls)
        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return (await session.execute(query)).scalars().all()

    @classmethod
    async def get(cls, pk: UUID, session: AsyncSession) -> "BaseModel":
        instance = await session.get(cls, pk)
        if instance is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{cls.verbose_name()} not found")

        return instance

    async def save(self, session: AsyncSession) -> "BaseModel":
        session.add(self)
        await session.commit()
        await session.refresh(self)

        return self

    @classmethod
    async def delete(cls, pk: UUID, session: AsyncSession) -> int:
        result = await session.execute(delete(cls).where(cls.pk == pk))
        if result.rowcount == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{cls.verbose_name()} not found")

        return result.rowcount
