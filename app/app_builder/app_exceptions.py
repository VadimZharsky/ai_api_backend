from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.exceptions import ServiceError
from app.tools.loggers import logger_hub


class AppExceptions:
    
    @staticmethod
    def include(app: FastAPI) -> None:
        @app.exception_handler(ServiceError)
        async def service_exception_handler(_: Request, exc: ServiceError) -> JSONResponse:
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": str(exc)},
            )

        @app.exception_handler(Exception)
        async def global_unknown_exception_handler(_: Request, exc: Exception) -> JSONResponse:
            logger_hub.service.error(f"exception: {exc!s}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )
