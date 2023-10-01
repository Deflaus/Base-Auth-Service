from typing import Any

from pydantic import BaseModel


class BaseKeySchema(BaseModel):
    prefix: str
    delimiter: str

    def get_key(self, *args: Any) -> str:
        return f"{self.prefix}{self.delimiter}{self.delimiter.join([str(arg) for arg in args])}"

    def get_key_parts(self, key: str) -> list[str]:
        return key.split(self.delimiter)
