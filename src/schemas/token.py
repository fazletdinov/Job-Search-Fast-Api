from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, EmailStr


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"

class TokenPayloadsBase(BaseModel):
    email: EmailStr
    role: list[str]
    exp: datetime

    @property
    def left_time(self):
        delta = datetime.now(timezone.utc) - self.exp
        return delta.seconds
    
class AccessTokenPayload(TokenPayloadsBase):
    pass

class RefreshTokenPayload(TokenPayloadsBase):
    session_id: str