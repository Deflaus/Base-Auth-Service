from passlib.context import CryptContext
from sqlalchemy import Boolean, Column, String, Text
from sqlalchemy.orm import validates

from models.postgres.mixins import CreatedAtUpdatedAtMixin, UUIDMixin


class PasswordService:
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def verify_password(cls, raw_password: str, hashed_password: str) -> bool:
        return cls.pwd_context.verify(raw_password, hashed_password)

    @classmethod
    def get_hashed_password(cls, password: str) -> str:
        return cls.pwd_context.hash(password)


class User(UUIDMixin, CreatedAtUpdatedAtMixin):
    __tablename__ = "users"

    username: str = Column(String(length=100), nullable=False, unique=True)
    password: str = Column(Text, nullable=False)
    full_name: str = Column(String(length=100), default=None, nullable=True)
    email: str = Column(String(length=100), default=None, nullable=True, unique=True)
    is_active: bool = Column(Boolean, default=False, nullable=False)

    def verify_password(self, raw_password: str) -> bool:
        return PasswordService.verify_password(raw_password, self.password)

    @validates("password")
    def validate_password(self, key, password):
        return PasswordService.get_hashed_password(password)
