from fastapi import HTTPException, status
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

BaseClass = declarative_base()


class BaseModel(BaseClass):  # type: ignore
    __abstract__ = True

    @classmethod
    def verbose_name(cls) -> str:
        return cls.__tablename__.capitalize()

    @classmethod
    async def get_list(cls, offset: int | None, limit: int | None, session: AsyncSession) -> list["BaseModel"]:
        query = select(cls)
        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return (await session.execute(query)).scalars().all()

    @classmethod
    async def get(cls, session: AsyncSession, raise_not_found: bool = True, **filter_kwargs) -> "BaseModel":
        query = select(cls)
        for arg_name, arg_value in filter_kwargs.items():
            query = query.where(getattr(cls, arg_name) == arg_value)

        instance = (await session.execute(query)).scalars().first()
        if instance is None and raise_not_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{cls.verbose_name()} not found")

        return instance

    async def save(self, session: AsyncSession) -> "BaseModel":
        session.add(self)
        await session.commit()
        await session.refresh(self)

        return self

    async def update(self, values_to_update: dict, session: AsyncSession) -> "BaseModel":
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

        await session.execute(update(self.__class__).values(new_values).where(self.__class__.pk == self.pk))
        await session.commit()
        await session.refresh(self)
        return self

    @classmethod
    async def delete(cls, session: AsyncSession, raise_not_found: bool = True, **filter_kwargs) -> int:
        query = delete(cls)
        for arg_name, arg_value in filter_kwargs.items():
            query = query.where(getattr(cls, arg_name) == arg_value)

        result = await session.execute(query)
        if result.rowcount == 0 and raise_not_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{cls.verbose_name()} not found")

        await session.commit()
        return result.rowcount
