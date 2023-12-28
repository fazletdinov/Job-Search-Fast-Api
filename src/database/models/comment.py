import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .vacansy import Vacansy
    from .user import User


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text: Mapped[str] = mapped_column(String(length=1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=datetime.utcnow,
                                                 server_default=func.now())
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                               ForeignKey("user.id",
                                                          ondelete="CASCADE",
                                                          onupdate="CASCADE"),
                                               nullable=False)
    vacansy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                                  ForeignKey("vacansy.id",
                                                             ondelete='CASCADE',
                                                             onupdate="CASCADE"),
                                                  nullable=False)
    owner: Mapped["User"] = relationship(back_populates="comments")
    vacansy: Mapped["Vacansy"] = relationship(back_populates="comments")

    def __repr__(self) -> str:
        return f"Comment: {self.id}"
