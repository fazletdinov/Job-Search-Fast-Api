import uuid
from datetime import datetime

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import String, DateTime, Column, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from database.session import Base, get_async_session
from src.users.service import SQLAlchemyUserDatabaseCustom


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(length=100), nullable=False, unique=True)
    password = Column(String(length=100), nullable=False)
    is_active = Column(Boolean, default=True)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_roles = relationship("UserRole",
                              back_populates="user",
                              cascade="all, delete",
                              passive_deletes=True)
    hrs = relationship("Hr", back_populates="user",
                       cascade="all, delete",
                       passive_deletes=True)
    resumes = relationship("Resume", back_populates="user",
                           cascade="all, delete",
                           passive_deletes=True)
    comments = relationship("Comment",
                            back_populates="owner",
                            cascade="all, delete",
                            passive_deletes=True)
    entries = relationship("Entry",
                           back_populates="user",
                           cascade="all, delete",
                           passive_deletes=True, )

    def __repr__(self) -> str:
        return f"User: {self.email}"


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(length=100), nullable=False, unique=True)
    user_roles = relationship("UserRole",
                              back_populates="role",
                              cascade="all, delete",
                              passive_deletes=True)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id,
                                                    ondelete="CASCADE",
                                                    onupdate="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.id,
                                                    ondelete="CASCADE",
                                                    onupdate="CASCADE"), nullable=False)
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class Entry(Base):
    __tablename__ = 'entry'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(
        User.id, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user_agent = Column(String(100))
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    refresh_token = Column(String(100))
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="entries")


class Hr(Base):
    __tablename__ = "hr"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(length=250), nullable=False, name="Имя")
    last_name = Column(String(length=250), nullable=False, name="Фамилия")
    middle_name = Column(
        String(length=250), nullable=False, name="Отчество")
    age = Column(Integer, nullable=False, name="Возраст")
    company_name = Column(String(length=250), nullable=False, name="Название компании")
    is_active = Column(Boolean, default=True)
    created = Column(
        DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id,
                                                    ondelete="CASCADE",
                                                    onupdate="CASCADE"), nullable=False)
    user = relationship("User", back_populates="hrs")
    vacansies = relationship("Vacansy",
                             cascade="all, delete",
                             back_populates="hr",
                             passive_deletes=True)

    def __repr__(self) -> str:
        return f"Resume: {self.first_name} - {self.last_name}"


class Resume(Base):
    __tablename__ = "resume"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(length=250), nullable=False, name="Имя")
    last_name = Column(String(length=250), nullable=False, name="Фамилия")
    middle_name = Column(
        String(length=250), nullable=False, name="Отчество")
    age = Column(Integer, nullable=False, name="Возраст")
    experience = Column(String(length=250), nullable=False, name="Опыт работы")
    education = Column(String(length=250), nullable=False, name="Образование")
    about = Column(String(length=3000), name="О себе")
    image = Column(String, name="Изображение", nullable=True)
    is_active = Column(Boolean, default=True)
    created = Column(
        DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id,
                                                    ondelete="CASCADE",
                                                    onupdate="CASCADE"), nullable=False)
    user = relationship("User", back_populates="resume")

    def __repr__(self) -> str:
        return f"Resume: {self.first_name} - {self.last_name}"


class Vacansy(Base):
    __tablename__ = "vacansy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_of_work = Column(
        String(length=250), nullable=False, name="Место работы")
    about_the_company = Column(String(length=3000), name="О компании")
    required_specialt = Column(
        String(length=500), nullable=False, name="Треубемая специальность")
    proposed_salary = Column(
        String(length=120), nullable=False, name="Заработная плата")
    working_conditions = Column(
        String(length=250), nullable=False, name="Рабочие условия")
    required_experience = Column(
        String(length=250), nullable=False, name="Требуемый опыт")
    is_active = Column(Boolean, default=True, name="Активна")
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    hr_id = Column(UUID(as_uuid=True), ForeignKey(Hr.id,
                                                  ondelete="CASCADE",
                                                  onupdate="CASCADE"), nullable=False)
    hr = relationship("Hr", back_populates="vacansies")
    comments = relationship("Comment",
                            back_populates="vacansy",
                            cascade='save-update, merge, delete',
                            passive_deletes=True)

    def __repr__(self) -> str:
        return f"Vacansy: {self.place_of_work} - {self.required_experience}"


class Comment(Base):
    __tablename__ = "comment"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(String(length=1000), nullable=False)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id,
                                                    ondelete="CASCADE",
                                                    onupdate="CASCADE"), nullable=False)
    vacansy_id = Column(UUID(as_uuid=True), ForeignKey(Vacansy.id,
                                                       ondelete='CASCADE',
                                                       onupdate="CASCADE"), nullable=False)
    owner = relationship("User", back_populates="comments")
    vacansy = relationship("Vacansy", back_populates="comments")

    def __repr__(self) -> str:
        return f"Comment: {self.id}"


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabaseCustom(session, User)
