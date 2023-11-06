from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from .comment import CommentResponse

class VacansyCreate(BaseModel):
    place_of_work: str
    about_the_company: str
    required_specialt: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str


class VacansyResponseAfterPost(BaseModel):
    id: int
    place_of_work: str
    about_the_company: str
    required_specialt: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str
    created: datetime

    class Config:
        from_attributes = True


class VacansyResponse(VacansyResponseAfterPost):
    comments: list[CommentResponse] | None = None


class VacansyResponseList(BaseModel):
    id: int
    place_of_work: str
    about_the_company: str
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
    about_the_company: str | None
    required_specialt: str | None
    proposed_salary: str | None
    working_conditions: str | None
    required_experience: str | None
    vacant: str | None
