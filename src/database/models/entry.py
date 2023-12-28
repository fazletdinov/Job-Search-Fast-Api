import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Entry(Base):
    __tablename__ = 'entry'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("user.id",
                                                          onupdate="CASCADE",
                                                          ondelete="CASCADE"),
                                               nullable=False)
    user_agent: Mapped[str] = mapped_column(String(length=100))
    date_time: Mapped[datetime] = mapped_column(default=datetime.utcnow,
                                                server_default=func.now())
    refresh_token: Mapped[str] = mapped_column(String(length=100))
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped["User"] = relationship(back_populates="entries")
