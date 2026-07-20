from sqlalchemy import exists, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.entities import User
from app.exceptions import DatabaseError
from app.tools.loggers import ILogger


class UserRepository:
    _SERV_NAME: str = "USER REPOSITORY"

    @staticmethod
    async def assert_user_exists(session: AsyncSession, user_id: int, logger: ILogger) -> bool:
        try:
            stmt = select(exists().where(User.id == user_id))
            is_exists: bool = await session.scalar(stmt) or False
            return is_exists
        except SQLAlchemyError as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> IS EXISTS >> SQLAlchemyError " +
                         f"<id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> IS EXISTS >> Exception " +
                f"<id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
    
    @staticmethod
    async def assert_user_exists_by_name(session: AsyncSession, username: str, logger: ILogger) -> bool:
        try:
            stmt = select(exists().where(User.username == username))
            is_exists: bool = await session.scalar(stmt) or False
            return is_exists
        except SQLAlchemyError as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> IS EXISTS BY NAME >> SQLAlchemyError " +
                f"<username>[{username}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> IS EXISTS BY NAME >> Exception " +
                f"<username>[{username}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def create(session: AsyncSession, entity: User, logger: ILogger) -> None:
        try:
            session.add(entity)
            await session.flush()
            await session.refresh(entity)
        except SQLAlchemyError as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> CREATE >> SQLAlchemyError " +
                         f"<name>[{entity.username}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> CREATE >> Exception " +
                f"<name>[{entity.username}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def get(session: AsyncSession, user_id: int, logger: ILogger) -> User | None:
        try:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
        except SQLAlchemyError as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> GET >> SQLAlchemyError " +
                         f"<id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> GET >> Exception " +
                f"<id>[{user_id}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex

    @staticmethod
    async def get_by_name(session: AsyncSession, username: str, logger: ILogger) -> User | None:
        try:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()
        except SQLAlchemyError as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> GET BY NAME >> SQLAlchemyError " +
                         f"<name>[{username}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
        except Exception as ex:
            logger.error(
                f"{UserRepository._SERV_NAME} >> GET BY NAME >> Exception " +
                f"<name>[{username}]<exc>[{ex!s}]"
            )
            raise DatabaseError(str(ex)) from ex
