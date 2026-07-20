from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.entities import Chat, Message
from app.exceptions import DatabaseError
from app.tools.loggers import ILogger


class MessageRepository:
    _SERV_NAME: str = "MESSAGE REPOSITORY"

    @staticmethod
    async def create(session: AsyncSession, entity: Message, logger: ILogger) -> None:
        try:
            session.add(entity)
            await session.flush()
            await session.refresh(entity)
        except SQLAlchemyError as ex:
            logger.error(
                f"{MessageRepository._SERV_NAME} >> CREATE >> SQLAlchemyError " +
                f"<chat_id>[{entity.chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{MessageRepository._SERV_NAME} >> CREATE >> Exception " +
                f"<chat_id>[{entity.chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def get_with_limit(session: AsyncSession, chat_id: int, limit: int, logger: ILogger) -> list[Message]:
        try:
            stmt = (
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            result = await session.execute(stmt)
            history_messages = list(result.scalars().all())
            history_messages.reverse()
            return history_messages
        except SQLAlchemyError as ex:
            logger.error(
                f"{MessageRepository._SERV_NAME} >> GET >> SQLAlchemyError <id>[{chat_id}]"
                + f"<chat_id>[{chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{MessageRepository._SERV_NAME} >> GET >> Exception <id>[{chat_id}]"
                + f"<chat_id>[{chat_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
