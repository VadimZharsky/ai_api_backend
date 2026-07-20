from starlette import status

from app.exceptions.service_exceptions import ServiceError


class LlmError(ServiceError):
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE
    detail: str = "token expired"