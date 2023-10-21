from datetime import datetime
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, DateTime, update, Column
from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi_users.models import UP
from fastapi import Depends

from database.session import Base, get_async_session


class SQLAlchemyUserDatabaseCustom(SQLAlchemyUserDatabase):
    """_summary_

    Args:
        SQLAlchemyUserDatabase (_type_): _description_
    Позволяет не удалять пользователя, а перевести его is_active=True в состояние False
    """
    async def delete(self, user: UP) -> None:
        query = update(User).\
            where(User.id == user.id, User.is_active == True).\
            values(is_active=False)
        await self.session.execute(query)
        await self.session.commit()


class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"


class User(SQLAlchemyBaseUserTableUUID, Base):
    created = Column(
        DateTime(timezone=True), default=datetime.utcnow)
    role = Column(String, default=Role.USER)

    def __repr__(self) -> str:
        return f"User: {self.email}"

    @property
    def is_admin(self):
        return self.role == Role.ADMIN

    @property
    def is_user(self):
        return self.role == Role.USER


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabaseCustom(session, User)
