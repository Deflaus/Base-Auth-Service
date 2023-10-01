import enum


class UserRolesEnum(str, enum.Enum):
    STAFF = "STAFF"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class HeaderKeyEnum(str, enum.Enum):
    ACCESS_TOKEN = "X-Access-Token"
    REFRESH_TOKEN = "X-Refresh-Token"
