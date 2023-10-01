from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql.schema import _NamingSchemaTD


class BaseModel(DeclarativeBase):
    pass


POSTGRES_INDEXES_NAMING_CONVENTION = _NamingSchemaTD(
    ix="%(column_0_label)s_idx",
    uq="%(table_name)s_%(column_0_name)s_key",
    ck="%(table_name)s_%(constraint_name)s_check",
    fk="%(table_name)s_%(column_0_name)s_fkey",
    pk="%(table_name)s_pkey",
)

BaseModel.metadata = MetaData(naming_convention=POSTGRES_INDEXES_NAMING_CONVENTION)
