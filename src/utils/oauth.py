from enum import Enum

from fastapi.param_functions import Form


class CookieKeyEnum(str, Enum):
    access_token = "access_token"
    refresh_token = "refresh_token"


class OAuth2PasswordRequestForm:
    def __init__(
        self,
        username: str = Form(),
        password: str = Form(),
    ):
        self.username = username
        self.password = password
