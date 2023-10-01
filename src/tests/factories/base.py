import typing

from factory import Factory
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.base import BaseModel


class BaseFactory(Factory):
    @classmethod
    def _create(cls, model_class, *args, **kwargs) -> typing.Coroutine[typing.Any, typing.Any, BaseModel]:
        async def create_coroutine(*args, **kwargs) -> BaseModel:
            session: AsyncSession = kwargs.pop("session")
            model = model_class(*args, **kwargs)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model

        return create_coroutine(*args, **kwargs)

    @classmethod
    async def create_batch(cls, size, **kwargs) -> list[typing.Any]:
        return [await cls.create(**kwargs) for _ in range(size)]
