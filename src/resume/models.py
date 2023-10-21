from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Column, Integer, UUID, Boolean
from sqlalchemy.orm import relationship

from database.session import Base
from src.users.models import User


class Resume(Base):
    __tablename__ = "resume"

    id = Column(Integer, primary_key=True)
    first_name = Column(String(length=250), nullable=False)
    last_name = Column(String(length=250), nullable=False)
    middle_name = Column(
        String(length=250), nullable=False)
    age = Column(Integer, nullable=False)
    experience = Column(String(length=250), nullable=False)
    education = Column(String(length=250), nullable=False)
    about = Column(String(length=3000))
    created = Column(
        DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="resumes")

    def __repr__(self) -> str:
        return f"Resume: {self.first_name} - {self.last_name}"
