import uuid
from datetime import datetime
from typing import Optional

from pydantic import EmailStr, BaseModel, Field
from fastapi_users import schemas
from fastapi_users import models


class UserRead(schemas.BaseUser[uuid.UUID]):
    id: models.ID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class ResumeCreate(BaseModel):
    first_name: str
    last_name: str
    middle_name: str
    age: int = Field(gt=0, lt=120)
    experience: str
    education: str
    about: str | None = Field(max_length=1000, default=None)


class ResumeRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: str
    age: int
    experience: str
    education: str
    about: str | None
    user_id: uuid.UUID

    class Config:
        from_attributes = True


class ResumeUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    middle_name: str | None
    age: int | None = Field(gt=0, lt=120)
    experience: str | None
    education: str | None
    about: str | None = Field(max_length=1)


class VacansyCreate(BaseModel):
    place_of_work: str
    required_specialty: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str

class VacansyRead(BaseModel):
    id: int
    place_of_work: str
    required_specialty: str
    proposed_salary: str
    working_conditions: str
    required_experience: str
    vacant: str
    created: datetime
    is_active: bool
    user_id: uuid.UUID

    class Config:
        from_attributes = True

class VacansyUpdate(BaseModel):
    place_of_work: str | None
    required_specialty: str | None
    proposed_salary: str | None
    working_conditions: str | None
    required_experience: str | None
    vacant: str | None