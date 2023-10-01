import typing
import uuid as _uuid

from pydantic import BaseModel, ConfigDict, Field


class BaseOrmSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class RedisModelSchema(BaseModel):
    pk: _uuid.UUID = Field(default_factory=_uuid.uuid4)


class BaseKeySchema(BaseModel):
    delimiter: str
    prefix: str

    def get_key(self, *args: typing.Any) -> str:
        return f"{self.prefix}{self.delimiter}" f"{self.delimiter.join(str(arg) for arg in args)}"


class RedisKeySchema(BaseKeySchema):
    delimiter: str = ":"
