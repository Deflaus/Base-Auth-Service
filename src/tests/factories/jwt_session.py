import datetime as dt

from factory.fuzzy import FuzzyDateTime

from db.models import JwtSession
from tests.factories.base import BaseFactory


class JwtSessionFactory(BaseFactory):
    expires_at = FuzzyDateTime(start_dt=dt.datetime.now(tz=dt.timezone.utc))

    class Meta:
        model = JwtSession
