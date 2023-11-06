from abc import ABC, abstractmethod
import bcrypt
from typing import List, Tuple
from functools import lru_cache
import logging

from fastapi import status, HTTPException, Depends
from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncSession

from database.token import TokenDBBase, get_token_db
from database.models import User as DBUser, Entry as DBEntry
from schemas import user as user_schema
from crud import user as user_dal, role as role_dal, entry as entry_dal, crud_social as user_socials_dal
from utils.token_manager import TokenManagerBase, get_token_manager
from database.session import get_db


class HashManagerBase(ABC):
    """Хэширование и проверка пароля"""
    @abstractmethod
    def hash_pwd(self, pwd: str) -> str:
        """Для получения hash пароля"""

    @abstractmethod
    def verify_pwd(self, pwd_in: str, pwd_hash: str) -> bool:
        """Проверка соответствия пароля"""

class AuthServiceBase(ABC):
    """Service для авторизации пользователя"""
    @abstractmethod
    async def register(self) -> DBUser:
        """Регистрация нового пользовател"""

    @abstractmethod
    async def login(self) -> tuple[str, str]:
        """Получение токенов доступа и обновления. Открытие новой сессии"""

    @abstractmethod
    async def logout(self) -> None:
        """Сбросьте токены доступа и обновите. Закрытие сессии"""

    @abstractmethod
    async def logout_all(self) -> None:
        """Закрытие сесси всех активных пользователей"""

    @abstractmethod
    async def refresh_tokens(self) -> tuple[str, str]:
           """Обновить refresh token и access"""

    @abstractmethod
    async def get_user_data(self) -> DBEntry:
        """Получение пользователя"""

    @abstractmethod
    async def get_user_role(self) -> str:
        """Получение role пользователя"""

    @abstractmethod
    async def update_user_data(self) -> DBUser:
        """Изменение пользовательсктх данных"""

    @abstractmethod
    async def update_user_password(self) -> None:
        """Изменение пароля пользователя"""

    @abstractmethod
    async def entry_history(self) -> list[DBEntry]:
        """Получить историю входа пользователя в систему"""

    @abstractmethod
    async def deactivate_user(self) -> None:
        """Деактивация пользователя"""

class AuthService(AuthServiceBase, HashManagerBase):

    def __init__(self,
                 token_db: TokenDBBase,
                 token_manager: TokenManagerBase,
                 user_db_session: AsyncSession) -> None:
        self.token_db = token_db
        self.token_manager = token_manager
        self.user_db_session = user_db_session

    def hash_pwd(self, pwd: str) -> str:
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(pwd.encode("utf-8"), salt)
        return pwd_hash.decode("utf-8")

    def verify_pwd(self, pwd_in: str, pwd_hash: str) -> bool:
        return bcrypt.checkpw(pwd_in.encode("utf-8"), pwd_hash.encode("utf-8"))
    
    async def register(self, user: user_schema.UserCreate, provider: str = None) -> DBUser:
        user_crud = user_dal.UserDAL(self.user_db_session)
        email_is_exist = user_crud.get_by_email(user.email)
        if email_is_exist:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь уже существует"
            )
        new_user = await user_crud.create(**user.model_dump(exclude={"password",}),
                                          password=self.hash_pwd(user.password.get_secret_value()))
        return new_user
          
