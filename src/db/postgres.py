from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import settings

engine = create_async_engine(settings().POSTGRES_DSN, echo=False, future=True)


def get_async_session():
    return sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_postgres() -> AsyncSession:
    async_session = get_async_session()
    async with async_session() as session:
        yield session
