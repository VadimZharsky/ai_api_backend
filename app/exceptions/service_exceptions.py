class ServiceError(Exception):
    status_code: int = 400
    detail: str = "Bad request"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.detail)
