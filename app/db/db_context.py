from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import MetaData, NullPool, event
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app_config import app_settings


class DbContext:
    def __init__(self) -> None:
        self.url: str = app_settings.DB.async_url
        self.echo: bool = app_settings.DB.ECHO
        self.echo_pool: bool = app_settings.DB.ECHO_POOL
        self.pool_size: int = app_settings.DB.POOL_SIZE
        self.max_overflow: int = app_settings.DB.MAX_OVERFLOW
        self.metadata: MetaData = MetaData(
            naming_convention=app_settings.DB.NAMING_KEYS_CONVENTION,
        )
        self._engine: AsyncEngine = create_async_engine(
            url=self.url,
            echo=self.echo,
            poolclass=NullPool,
            connect_args={"timeout": 30},
        )

        @event.listens_for(self._engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute("PRAGMA journal_mode=WAL;")
            cursor.execute("PRAGMA synchronous=NORMAL;")
            cursor.close()

        self.async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_async_session(self) -> AsyncSession:
        return self.async_session_maker()

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession]:
        async with self.async_session_maker() as session:
            yield session


db_context = DbContext()
