from uuid import UUID

from pydantic import (BaseModel,
                      EmailStr,
                      SecretStr,
                      Field,
                      ConfigDict,
                      field_validator,
                      model_validator)


def _pwd_validator(value: str) -> str:
    min_len = 3
    if len(value) < min_len:
        raise ValueError("пароль должен содержать не менее 3 символов")
    if value.isdigit() or value.isalpha():
        raise ValueError(
            "пароль должен содержать буквы, цифры и специальные символы")


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def pwd_validator(cls, value: SecretStr) -> SecretStr:
        return SecretStr(_pwd_validator(value.get_secret_value()))


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)


class ChangeUserData(BaseModel):
    email: EmailStr = None


class ChangeUserPassword(BaseModel):
    old_password: SecretStr
    new_password: SecretStr

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.old_password.get_secret_value() == self.new_password.get_secret_value():
            raise ValueError("Новый пароль не должен совпадать со старым")
        return self
    




