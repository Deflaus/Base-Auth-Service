from pydantic import BaseModel

from utils.json import OrjsonConfig


class TokenPairSchema(BaseModel):
    class Config(OrjsonConfig):
        pass

    access: str
    refresh: str
    expires_in: int | None
