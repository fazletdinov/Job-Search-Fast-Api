from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr


class ChangeUserData(BaseModel):
    email: EmailStr = None


class ChangeUserPassword(BaseModel):
    old_password: SecretStr
    new_password: SecretStr
