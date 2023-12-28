import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Resume(Base):
    __tablename__ = "resume"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(length=250))
    last_name: Mapped[str] = mapped_column(String(length=250))
    middle_name: Mapped[str] = mapped_column(String(length=250))
    age: Mapped[int]
    experience: Mapped[str] = mapped_column(String(length=250))
    education: Mapped[str] = mapped_column(String(length=250))
    about: Mapped[str] = mapped_column(String(length=3000))
    image: Mapped[str | None]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=datetime.utcnow,
                                                 server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("user.id",
                                                          ondelete="CASCADE",
                                                          onupdate="CASCADE"),
                                               nullable=False)
    user: Mapped["User"] = relationship(back_populates="resumes")

    def __repr__(self) -> str:
        return f"Resume: {self.first_name} - {self.last_name}"
