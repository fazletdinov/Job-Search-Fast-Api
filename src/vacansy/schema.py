from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommentCreate(BaseModel):
    text: str


class CommentUpdate(BaseModel):
    text: str | None


class CommentRead(BaseModel):
    id: int
    text: str
    created: datetime

    class Config:
        from_attributes = True


class VacansyCreate(BaseModel):
    place_of_work: str
    required_specialt: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str


class VacansyReadAfterPost(BaseModel):
    id: int
    place_of_work: str
    required_specialt: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str
    created: datetime

    class Config:
        from_attributes = True


class VacansyRead(VacansyReadAfterPost):
    comments: list[CommentRead] | None = None


class VacansyReadList(BaseModel):
    id: int
    place_of_work: str
    required_specialt: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str
    created: datetime

    class Config:
        from_attributes = True


class VacansyUpdate(BaseModel):
    place_of_work: str | None
    required_specialt: str | None
    proposed_salary: str | None
    working_conditions: str | None
    required_experience: str | None
    vacant: str | None
