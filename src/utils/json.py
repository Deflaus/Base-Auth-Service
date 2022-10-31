from typing import Any

import orjson


def orjson_dumps(v: Any, *, default: Any) -> str:
    return orjson.dumps(v, default=default).decode()


class OrjsonConfig:
    json_loads = orjson.loads
    json_dumps = orjson_dumps
