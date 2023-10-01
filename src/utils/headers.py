from fastapi.security import APIKeyHeader as FastAPIAPIKeyHeader
from starlette.requests import Request

from exceptions import HeaderIsNotProvidedException


class APIKeyHeader(FastAPIAPIKeyHeader):
    async def __call__(self, request: Request) -> str | None:
        api_key = request.headers.get(self.model.name)
        if not api_key:
            if self.auto_error:
                raise HeaderIsNotProvidedException(header=self.model.name)
            else:
                return None
        return api_key
