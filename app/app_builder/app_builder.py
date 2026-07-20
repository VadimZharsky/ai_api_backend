from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from app.app_builder.app_exceptions import AppExceptions
from app.app_builder.app_routers import AppRouters
from app.app_builder.middlewares import Middlewares
from app.dependencies.functions import openai_client
from app.tools.loggers import logger_hub
from app_config import AppConstants


class AppBuilder:
    @staticmethod
    def build() -> FastAPI:
        @asynccontextmanager
        async def lifespan(_: Any) -> AsyncGenerator[None, Any]:
            logger_hub.initialize()
            yield

            await openai_client.close()

        current_app = FastAPI(
            title=AppConstants.TITLE,
            version=AppConstants.VERSION,
            lifespan=lifespan,
        )
        AppRouters.include(app=current_app)
        Middlewares.include(app=current_app)
        AppExceptions.include(app=current_app)

        return current_app
