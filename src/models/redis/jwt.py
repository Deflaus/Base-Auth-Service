from models.redis.base import RedisJsonModel, RedisKeySchema


class JwtPublicKey(RedisJsonModel):
    _key_schema: RedisKeySchema = RedisKeySchema(prefix="jwt_public_key")
    public_key: str
