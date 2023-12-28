import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .comment import Comment
    from .hr import Hr
    from .resume import Resume
    from .entry import Entry
    from .user_role import UserRole


class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(length=100), unique=True)
    password: Mapped[str] = mapped_column(String(length=100))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=datetime.utcnow,
                                                 server_default=func.now())
    user_roles: Mapped[list["UserRole"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True)
    hrs: Mapped[list["Hr"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True)
    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True)
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="owner",
        cascade="all, delete",
        passive_deletes=True)
    entries: Mapped[list["Entry"]] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True, )

    def __repr__(self) -> str:
        return f"User ({self.id}, {self.email})"
