import uuid

from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
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
    async def get(cls, pk: uuid.UUID, session: AsyncSession, raise_not_found: bool = True) -> "BaseModel":
        instance = await session.get(cls, pk)
        if instance is None and raise_not_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{cls.verbose_name()} not found")

        return instance

    async def save(self, session: AsyncSession) -> "BaseModel":
        session.add(self)
        await session.commit()
        await session.refresh(self)

        return self

    async def update(self, pk: uuid.UUID, values_to_update: dict, session: AsyncSession) -> "BaseModel":
        new_values: dict = {}
        for field, value in values_to_update.items():
            try:
                model_field_value = getattr(self, field)
            except AttributeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Field {field} not found",
                )

            if model_field_value == value or value is None:
                continue

            new_values[field] = value

        if not new_values:
            return self

        query = update(self.__class__).values(new_values).where(self.__class__.pk == pk)
        await session.execute(query)
        await session.commit()
        return self

    @classmethod
    async def delete(cls, pk: uuid.UUID, session: AsyncSession, raise_not_found: bool = True) -> int:
        result = await session.execute(delete(cls).where(cls.pk == pk))
        if result.rowcount == 0 and raise_not_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{cls.verbose_name()} not found")

        await session.commit()
        return result.rowcount
