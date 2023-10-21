from pydantic import BaseModel, Field


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