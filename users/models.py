from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, String, DateTime, update
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from fastapi_users.db import SQLAlchemyUserDatabase
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


class User(SQLAlchemyBaseUserTableUUID, Base):
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="user")
    vacansies: Mapped[list["Vacansy"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User: {self.email}"


class Resume(Base):
    __tablename__ = "resume"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(length=250), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=250), nullable=False)
    middle_name: Mapped[str] = mapped_column(
        String(length=250), nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    experience: Mapped[str] = mapped_column(String(length=250), nullable=False)
    education: Mapped[str] = mapped_column(String(length=250), nullable=False)
    about: Mapped[str] = mapped_column()
    created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="resumes")

    def __repr__(self) -> str:
        return f"Resume: {self.first_name} - {self.last_name}"


class Vacansy(Base):
    __tablename__ = "vacansy"

    id: Mapped[int] = mapped_column(primary_key=True)
    place_of_work: Mapped[str] = mapped_column(
        String(length=250), nullable=False)
    required_specialty: Mapped[str] = mapped_column(
        String(length=500), nullable=False)
    proposed_salary: Mapped[str] = mapped_column(
        String(length=120), nullable=False)
    working_conditions: Mapped[str] = mapped_column(
        String(length=250), nullable=False)
    required_experience: Mapped[str] = mapped_column(
        String(length=250), nullable=False)
    vacant: Mapped[str] = mapped_column(String(length=20), default="Yes")
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(default=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="vacansies")

    def __repr__(self) -> str:
        return f"Vacansy: {self.place_of_work} - {self.required_experience}"


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabaseCustom(session, User)
