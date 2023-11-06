from datetime import datetime

from pydantic import BaseModel


class CommentCreate(BaseModel):
    text: str


class CommentUpdate(BaseModel):
    text: str | None


class CommentResponse(BaseModel):
    id: int
    text: str
    created: datetime

    class Config:
        from_attributes = True