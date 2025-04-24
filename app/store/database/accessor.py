import typing

from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.base.base_accessor import BaseAccessor

if typing.TYPE_CHECKING:
    from aiohttp.web import Application


class DatabaseAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)

        self.engine: AsyncEngine | None = None
        self.session: AsyncSession | None = None
        self.config = self.app.config.database

    async def connect(self):
        self.engine = create_async_engine(
            URL.create(
                drivername="postgresql+asyncpg",
                username=self.config.username,
                password=self.config.password,
                host=self.config.host,
                database=self.config.database,
            ),
            # echo=True
        )
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)
        self.app.log.info("Connected '%s'", self.__class__.__name__)

    async def disconnect(self):
        await self.engine.dispose()
        self.app.log.info("Disconnected '%s'", self.__class__.__name__)
