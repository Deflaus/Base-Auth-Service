from db.repositories.base import BaseRedisRepository
from schemas.base import RedisKeySchema
from schemas.jwt import JwtPublicKeySchema


class JwtPublicKeyRepository(BaseRedisRepository):
    _key_schema = RedisKeySchema(prefix="jwt_public_key")
    _model_schema = JwtPublicKeySchema
