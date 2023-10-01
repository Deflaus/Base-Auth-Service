from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from fastapi import FastAPI
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.router import api_router
from db.redis import get_redis_connection
from db.repositories.jwt import JwtPublicKeyRepository
from exceptions import (
    BadRequestException,
    ForbiddenException,
    MessageException,
    NotFoundException,
    UnauthorizedException,
)
from schemas.jwt import JwtPublicKeySchema
from settings import get_settings


async def save_jwt_key(key: RSAPrivateKey = rsa.generate_private_key(public_exponent=65537, key_size=2048)):
    settings = get_settings()

    settings.TOKEN_PRIVATE_KEY = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()
    async with get_redis_connection() as redis:
        jwt_public_key_repository = JwtPublicKeyRepository(redis_client=redis)

        jwt_public_key = JwtPublicKeySchema(
            pk=settings.TOKEN_PUBLIC_KEY_PK,
            public_key=key.public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
            .decode(),
        )
        await jwt_public_key_repository.save(instance=jwt_public_key)


async def message_exception_handler(_: Request, exc: MessageException):
    exception_classes_to_status_code_map = {
        BadRequestException: status.HTTP_400_BAD_REQUEST,
        UnauthorizedException: status.HTTP_401_UNAUTHORIZED,
        ForbiddenException: status.HTTP_403_FORBIDDEN,
        NotFoundException: status.HTTP_404_NOT_FOUND,
    }

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    for exception_class, exception_status_code in exception_classes_to_status_code_map.items():
        if isinstance(exc, exception_class):
            status_code = exception_status_code

    return JSONResponse(status_code=status_code, content={"error": exc.message})


def get_app() -> FastAPI:
    app = FastAPI(
        title="Base Auth Service",
        openapi_url="/api/openapi.json",
        docs_url="/api/swagger",
    )

    app.include_router(api_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_allow_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(MessageException, message_exception_handler)

    app.add_event_handler("startup", save_jwt_key)

    return app


app = get_app()
