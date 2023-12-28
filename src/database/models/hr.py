import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .vacansy import Vacansy


class Hr(Base):
    __tablename__ = "hr"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(length=250))
    last_name: Mapped[str] = mapped_column(String(length=250))
    middle_name: Mapped[str] = mapped_column(
        String(length=250))
    age: Mapped[int]
    company_name: Mapped[str] = mapped_column(String(length=250))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        server_default=func.now(),
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("user.id",
                                                          ondelete="CASCADE",
                                                          onupdate="CASCADE"),
                                               nullable=False)
    user: Mapped["User"] = relationship(back_populates="hrs")
    vacansies: Mapped[list["Vacansy"]] = relationship(
        cascade="all, delete",
        back_populates="hr",
        passive_deletes=True)
