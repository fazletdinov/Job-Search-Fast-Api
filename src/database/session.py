from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = True, future: bool = True) -> None:
        print("url = ", url)
        self.engine = create_async_engine(url=url, echo=echo, future=future)
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            yield session


db_helper = DatabaseHelper(
    url=settings.db.async_url,
    echo=settings.db.echo,
    future=settings.db.future,
)
