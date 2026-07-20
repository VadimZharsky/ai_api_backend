from starlette import status

from app.exceptions.service_exceptions import ServiceError


class EntityNotFoundError(ServiceError):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "entity not found"
