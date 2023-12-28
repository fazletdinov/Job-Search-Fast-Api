import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from .base import Base

if TYPE_CHECKING:
    from .hr import Hr
    from .comment import Comment


class Vacansy(Base):
    __tablename__ = "vacansy"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    place_of_work: Mapped[str] = mapped_column(String(length=250))
    about_the_company: Mapped[str] = mapped_column(String(length=3000))
    required_specialt: Mapped[str] = mapped_column(String(length=500))
    proposed_salary: Mapped[str] = mapped_column(String(length=120))
    working_conditions: Mapped[str] = mapped_column(String(length=250))
    required_experience: Mapped[str] = mapped_column(String(length=250))
    is_active: Mapped[bool] = mapped_column(default=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                              default=datetime.utcnow,
                                              server_default=func.now())
    hr_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True),
                                             ForeignKey("hr.id",
                                                        ondelete="CASCADE",
                                                        onupdate="CASCADE"),
                                             nullable=False)
    hr: Mapped["Hr"] = relationship(back_populates="vacansies")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="vacansy",
        cascade='save-update, merge, delete',
        passive_deletes=True)

    def __repr__(self) -> str:
        return f"Vacansy: {self.place_of_work} - {self.required_experience}"
