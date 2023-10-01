from factory import LazyAttribute

from db.models import User
from services.auth import AuthService
from tests.factories.base import BaseFactory
from tests.factories.fakers import UniqueStringFaker
from tests.utils import get_random_str


class UserFactory(BaseFactory):
    username = UniqueStringFaker("user_name")
    full_name = UniqueStringFaker("first_name")
    email = UniqueStringFaker("email")
    password = LazyAttribute(lambda _: AuthService.hash_password(get_random_str()))

    class Meta:
        model = User
