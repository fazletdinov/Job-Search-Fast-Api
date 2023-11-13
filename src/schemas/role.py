from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class RoleResponse(BaseModel):
    id: UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class RequestRole(BaseModel):
    name: str = Field()


class RequestNewRoleToUser(BaseModel):
    user_id: UUID = Field()
    role_id: UUID = Field()


class UUIDMixIn(BaseModel):
    id: UUID = Field(..., alias="uuid")

    class Config:
        allow_population_by_field_name = True


class ResponseRole(UUIDMixIn):
    name: str = Field()
