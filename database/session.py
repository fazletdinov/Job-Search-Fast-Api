from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.core.config import db_settings

engine = create_async_engine(db_settings.async_url, future=True, echo=True)

async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session
