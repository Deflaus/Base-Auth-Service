import typing


class MessageException(Exception):
    message: str


class NotFoundException(MessageException):
    pass


class BadRequestException(MessageException):
    pass


class UnauthorizedException(MessageException):
    pass


class ForbiddenException(MessageException):
    pass


class UserNotFoundException(NotFoundException):
    message = "User not found"


class InvalidPasswordException(BadRequestException):
    message = "Invalid password"


class TokenIsExpiredException(UnauthorizedException):
    message = "Token is expired"


class TokenDecodeException(UnauthorizedException):
    def __init__(self, error: typing.Any) -> None:
        self.message = f"Token decode error: {error}"


class OperationNotPermittedException(ForbiddenException):
    message = "Operation not permitted"


class HeaderIsNotProvidedException(UnauthorizedException):
    def __init__(self, header: str) -> None:
        self.message = f"Header {header} is not provided"


class CreateUserException(MessageException):
    message = "Create user error"
