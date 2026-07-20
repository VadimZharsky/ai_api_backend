from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.llm import ILlmClient, OpenaiClient
from app.db import db_context
from app.services import AuthService, ChatService
from app.tools.loggers import ILogger, logger_hub

openai_client = OpenaiClient(logger=logger_hub.service)


def get_service_logger() -> ILogger:
    return logger_hub.service

async def get_db() -> AsyncIterator[AsyncSession]:
    async with db_context.async_session_maker() as session:
        yield session

def get_openai_client() -> ILlmClient:
    return openai_client

def get_auth_service(
    logger: Annotated[ILogger, Depends(get_service_logger)],
    session: Annotated[AsyncSession, Depends(get_db)]
) -> AuthService:
    return AuthService(
        logger=logger,
        session=session,
    )

def get_chat_service(
    logger: Annotated[ILogger, Depends(get_service_logger)],
    session: Annotated[AsyncSession, Depends(get_db)],
    llm_client: Annotated[ILlmClient, Depends(get_openai_client)],
) -> ChatService:
    return ChatService(
        session=session,
        logger=logger,
        llm_client=llm_client,
    )
