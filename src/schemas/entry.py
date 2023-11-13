from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EntryCreate(BaseModel):
    user_id: UUID
    user_agnet: str = None
    refresh_token: str = None


class EntryResponse(BaseModel):
    user_agent: str = None
    date_time: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)