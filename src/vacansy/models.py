from datetime import datetime

from sqlalchemy import ForeignKey, String, DateTime, Column, Integer, UUID, Boolean
from sqlalchemy.orm import relationship

from database.session import Base
from src.users.models import User


class Vacansy(Base):
    __tablename__ = "vacansy"

    id = Column(Integer, primary_key=True)
    place_of_work = Column(
        String(length=250), nullable=False)
    required_specialt = Column(
        String(length=500), nullable=False)
    proposed_salary = Column(
        String(length=120), nullable=False)
    working_conditions = Column(
        String(length=250), nullable=False)
    required_experience = Column(
        String(length=250), nullable=False)
    vacant = Column(String(length=20), default="Yes")
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    user = relationship("User", backref="vacansies")
    comments = relationship("Comment", back_populates="vacansy", cascade='save-update, merge, delete',
        passive_deletes=True)

    def __repr__(self) -> str:
        return f"Vacansy: {self.place_of_work} - {self.required_experience}"


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    text = Column(String(length=1000), nullable=False)
    created = Column(DateTime(timezone=True), default=datetime.utcnow)
    user_id = Column(UUID, ForeignKey("user.id"), nullable=False)
    vacansy_id = Column(Integer, ForeignKey("vacansy.id", ondelete='CASCADE'), nullable=False)
    owner = relationship("User", backref="comments")
    vacansy = relationship(Vacansy, back_populates="comments")

    def __repr__(self) -> str:
        return f"Comment: {self.id}"
