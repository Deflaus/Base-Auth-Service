from schemas.base import RedisModelSchema


class JwtPublicKeySchema(RedisModelSchema):
    public_key: str
