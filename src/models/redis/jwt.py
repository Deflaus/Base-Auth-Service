from models.redis.base import RedisJsonModel


class JwtPublicKey(RedisJsonModel):
    public_key: bytes
