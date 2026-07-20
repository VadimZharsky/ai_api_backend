from collections.abc import Sequence

from sqlalchemy import RowMapping, Select, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.entities import Chat
from app.exceptions import DatabaseError
from app.models.request_schemas import ChatSortBy, GetChatsInfoParams, OrderBy
from app.tools.loggers import ILogger


class ChatRepository:
    _SERV_NAME: str = "CHAT REPOSITORY"

    @staticmethod
    async def create(session: AsyncSession, entity: Chat, logger: ILogger) -> None:
        try:
            session.add(entity)
            await session.flush()
            await session.refresh(entity)
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> CREATE >> SQLAlchemyError " +
                         f"<name>[{entity.title}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> CREATE >> Exception " +
                f"<name>[{entity.title}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def update(session: AsyncSession, entity: Chat, logger: ILogger) -> None:
        try:
            await session.flush()
            await session.refresh(entity)
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> UPDATE >> SQLAlchemyError " +
                f"<id>[{entity.id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> UPDATE >> Exception " +
                f"<id>[{entity.id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def get(session: AsyncSession, user_id: int, chat_id: int, logger: ILogger) -> Chat | None:
        try:
            result = await session.execute(
                select(Chat)
                .where(Chat.id == chat_id, Chat.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET >> SQLAlchemyError <id>[{chat_id}]" +
                f"<user_id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET >> Exception <id>[{chat_id}]"
                + f"<user_id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def get_chats_info_by_user_id(
        session: AsyncSession, user_id: int, params: GetChatsInfoParams, logger: ILogger
    ) -> Sequence[RowMapping]:
        try:
            stmt = (
                select(Chat.id, Chat.title)
                .where(Chat.user_id == user_id)
                .select_from(Chat)
            )
            stmt = ChatRepository._apply_sort(query=stmt, params=params)
            result = await session.execute(stmt)
            return result.mappings().all()
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET CHATS INFO >> SQLAlchemyError " +
                f"<user_id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET CHATS INFO >> Exception "
                + f"<user_id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def refresh_chat_updated_at_time(session: AsyncSession, chat_id: int, logger: ILogger) -> None:
        try:
            stmt = (
                update(Chat)
                .where(Chat.id == chat_id)
                .values(updated_at=func.now())
            )
            _ = await session.execute(stmt)
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> REFRESH CHAT UPDATE AT TIME >> SQLAlchemyError " +
                f"<chat_id>[{chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> REFRESH CHAT UPDATE AT TIME >> Exception "
                + f"<chat_id>[{chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def refresh_chat_updated_at_time_with_prompt(
        session: AsyncSession,
        chat_id: int,
        prompt: str,
        logger: ILogger
    ) -> None:
        try:
            stmt = (
                update(Chat)
                .where(Chat.id == chat_id)
                .values(updated_at=func.now(), prompt=prompt)
            )
            _ = await session.execute(stmt)
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> REFRESH CHAT UPDATE AT TIME >> SQLAlchemyError " +
                f"<chat_id>[{chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> REFRESH CHAT UPDATE AT TIME >> Exception "
                + f"<chat_id>[{chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def get_chat_with_history(
        session: AsyncSession, user_id: int, chat_id: int, logger: ILogger
    ) -> Chat | None:
        try:
            result = await session.execute(
                select(Chat)
                .where(Chat.id == chat_id, Chat.user_id == user_id)
                .options(selectinload(Chat.messages))
            )
            chat: Chat | None = result.scalar_one_or_none()
            if chat:
                chat.messages.sort(key=lambda x: x.id)
            return chat
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET WITH HISTORY >> SQLAlchemyError <id>[{chat_id}]" +
                f"<user_id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET WITH HISTORY >> Exception <id>[{chat_id}]"
                + f"<user_id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
    
    @staticmethod
    async def delete(session: AsyncSession, entity: Chat, logger: ILogger) -> None:
        try:
            await session.delete(entity)
            await session.flush()
        except SQLAlchemyError as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET WITH HISTORY >> SQLAlchemyError <id>[{entity.id}]"
                + f"<user_id>[{entity.user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{ChatRepository._SERV_NAME} >> GET WITH HISTORY >> Exception <id>[{entity.id}]"
                + f"<user_id>[{entity.user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex


    @staticmethod
    def _apply_sort(query: Select[tuple[int, str]], params: GetChatsInfoParams) -> Select[tuple[int, str]]:
        match params.sort_by:
            case ChatSortBy.DATETIME:
                column = Chat.updated_at
            case _:
                column = Chat.id
        if params.order_by == OrderBy.ASC:
            return query.order_by(column.asc())
        return query.order_by(column.desc())
