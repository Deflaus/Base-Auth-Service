import calendar
import datetime as dt
import uuid

from jose import jwt
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError

from db.postgres import get_engine
from schemas.auth import AccessTokenPayloadSchema, RefreshTokenPayloadSchema
from services.auth import AuthService
from settings import get_settings


def get_random_str() -> str:
    return str(uuid.uuid4())


def get_refresh_token(
    user_uuid: uuid.UUID,
    is_expired: bool = False,
) -> tuple[str, dt.datetime]:
    settings = get_settings()

    refresh_token_expire_delta = dt.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    if is_expired is False:
        refresh_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) + refresh_token_expire_delta

    else:
        refresh_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) - refresh_token_expire_delta

    token_payload = RefreshTokenPayloadSchema(
        sub=str(user_uuid),
        exp=calendar.timegm(refresh_token_expires_at.utctimetuple()),
    )

    encoded_jwt = jwt.encode(
        claims=token_payload.model_dump(),
        key=settings.TOKEN_PRIVATE_KEY,
        algorithm=AuthService._jwt_algorithm,
    )

    return encoded_jwt, refresh_token_expires_at


def get_access_token(
    user_uuid: uuid.UUID,
    is_expired: bool = False,
) -> tuple[str, dt.datetime]:
    settings = get_settings()

    access_token_expire_delta = dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    if is_expired is False:
        access_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) + access_token_expire_delta

    else:
        access_token_expires_at = dt.datetime.now(tz=dt.timezone.utc) - access_token_expire_delta

    token_payload = AccessTokenPayloadSchema(
        sub=str(user_uuid),
        exp=calendar.timegm(access_token_expires_at.utctimetuple()),
    )

    encoded_jwt = jwt.encode(
        claims=token_payload.model_dump(),
        key=settings.TOKEN_PRIVATE_KEY,
        algorithm=AuthService._jwt_algorithm,
    )

    return encoded_jwt, access_token_expires_at


async def create_database(url: str) -> None:
    url_object = make_url(url)
    database = url_object.database
    url_object = url_object.set(database="postgres")

    engine = get_engine(url=url_object, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        await conn.execute(text(f'CREATE DATABASE "{database}" ENCODING "utf8"'))

    await engine.dispose()


async def database_exists(url: str) -> bool:
    url_object = make_url(url)
    database = url_object.database
    url_object = url_object.set(database="postgres")

    engine = None
    try:
        engine = get_engine(url=url_object, isolation_level="AUTOCOMMIT")
        async with engine.begin() as conn:
            try:
                datname_exists = await conn.scalar(text(f"SELECT 1 FROM pg_database WHERE datname='{database}'"))

            except (ProgrammingError, OperationalError):
                datname_exists = 0

        return bool(datname_exists)

    finally:
        if engine:
            await engine.dispose()


async def drop_database(url: str) -> None:
    url_object = make_url(url)
    database = url_object.database
    url_object = url_object.set(database="postgres")

    engine = get_engine(url=url_object, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        disc_users = f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}' AND pid <> pg_backend_pid();
        """
        await conn.execute(text(disc_users))

        await conn.execute(text(f'DROP DATABASE "{database}"'))

    await engine.dispose()
