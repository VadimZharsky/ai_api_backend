from starlette import status

from app.exceptions.service_exceptions import ServiceError


class UserAlreadyExistsError(ServiceError):
    status_code: int = status.HTTP_409_CONFLICT
    detail: str = "user already exists"


class UserNotFoundError(ServiceError):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "user not found"
    
    
class UserDeactivatedError(ServiceError):
    status_code: int = status.HTTP_403_FORBIDDEN
    detail: str = "user deactivated"


class InvalidUsernameOrPasswordError(ServiceError):
    status_code: int = status.HTTP_403_FORBIDDEN
    detail: str = "invalid username or password"
