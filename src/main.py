from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from fastapi import FastAPI
from pydantic import SecretStr

from api import api_router
from core.settings import settings
from models.redis.jwt import JwtPublicKey

app = FastAPI(title="Base Auth Service")
app.include_router(api_router)


async def save_jwt_key(key: RSAPrivateKey = rsa.generate_private_key(public_exponent=65537, key_size=2048)):
    settings().TOKEN_PRIVATE_KEY = SecretStr(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode()
    )
    await JwtPublicKey(
        pk=settings().TOKEN_PUBLIC_KEY_PK,
        public_key=key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo
        ),
    ).save()


@app.on_event("startup")
async def startup():
    await save_jwt_key()
