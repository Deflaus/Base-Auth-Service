from schemas.base import BaseSchema


class User(BaseSchema):
    username: str
    email: str | None
    full_name: str | None
    is_active: bool | None


class UserInDB(User):
    hashed_password: str
