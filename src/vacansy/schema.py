from datetime import datetime

from pydantic import BaseModel


class VacansyCreate(BaseModel):
    place_of_work: str
    required_specialt: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str

class VacansyRead(BaseModel):
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