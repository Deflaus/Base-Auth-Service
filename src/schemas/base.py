from pydantic import BaseModel

from utils.json import OrjsonConfig


class BaseSchema(BaseModel):
    class Config(OrjsonConfig):
        pass
