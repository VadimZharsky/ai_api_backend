import http
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.cors import CORSMiddleware

from app.tools.loggers import logger_hub


class Middlewares:
    @staticmethod
    def include(app: FastAPI) -> None:
        @app.middleware("http")
        async def add_process_time_header(
            request: Request,
            call_next: Callable[[Request], Awaitable[Response]]
        ) -> Response:
            start_time = time.time()
            response = await call_next(request)
            url = f"{request.url.path}?{request.query_params}" if request.query_params else request.url.path
            process_time = (time.time() - start_time) * 1000
            formatted_process_time = f"{process_time:.2f}"
            host: str | None = None
            port: int | None = None
            if request.client:
                host = request.client.host
                port = request.client.port
            try:
                status_phrase = http.HTTPStatus(response.status_code).phrase
            except ValueError:
                status_phrase = ""
            logger_hub.api.info(
                f'{host}:{port} - "{request.method} {url}" {response.status_code} {status_phrase} ' +
                f'{formatted_process_time} ms'
            )
            response.headers["X-Process-Time"] = f"{formatted_process_time} ms"
            return response

        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
