from fastapi import FastAPI

from app.api import auth_router, chat_router


class AppRouters:
    @staticmethod
    def include(app: FastAPI) -> None:
        app.include_router(router=auth_router)
        app.include_router(router=chat_router)
