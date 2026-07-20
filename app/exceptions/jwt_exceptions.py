from starlette import status

from app.exceptions.service_exceptions import ServiceError


class TokenExpiredError(ServiceError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "token expired"

class TokenNotFoundError(ServiceError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "token not found"


class InvalidTokenError(ServiceError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "invalid token"

class MismatchTokenError(ServiceError):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "refresh_token does not match"
