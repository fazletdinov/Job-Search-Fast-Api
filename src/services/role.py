import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional
import logging
import logging.config

from fastapi import status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.role import RoleDAL
from src.crud.user_role import UserRoleDAL
from src.crud.user import UserDAL
from database.session import get_async_session
from src.schemas.role import ResponseRole
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class RoleServiceBase(ABC):

    @abstractmethod
    async def create_role(self, role_name: str) -> Optional[ResponseRole]:
        """Создание новой роли"""

    @abstractmethod
    async def read_role(self, role_id: uuid.UUID) -> Optional[ResponseRole]:
        """Чтение роли из БД"""

    @abstractmethod
    async def read_roles(self) -> Optional[list[ResponseRole]]:
        """Получение списка ролей"""

    @abstractmethod
    async def update_role(self, role_id: uuid.UUID, new_name: str) -> Optional[ResponseRole]:
        """Обновление роли"""

    @abstractmethod
    async def delete_role(self, role_id: uuid.UUID) -> uuid.UUID | None:
        """Удаление роли"""

    @abstractmethod
    async def get_user_access_area(self, user_id: uuid.UUID) -> ResponseRole | list[ResponseRole]:
        """Получить область доступа для пользователя по его идентификатору"""

    @abstractmethod
    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Установите новую или дополнительную роль для пользователя"""

    @abstractmethod
    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Удалить роль из ролей пользователей"""


class RoleService(RoleServiceBase):
    def __init__(self, db_session: AsyncSession):
        log.info("Инициализация role service")
        self.db_session = db_session

    async def create_role(self, role_name: str) -> ResponseRole | None:
        async with self.db_session as session:
            async with session.begin():
                role_crud = RoleDAL(session)
                role_exists = await role_crud.get_by_name(role_name)
                if role_exists:
                    log.error(
                        f"{status.HTTP_400_BAD_REQUEST}: Эта роль существует")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Эта роль существует"
                    )
                log.debug("Создание новой role")
                role = await role_crud.create(name=role_name)
                return ResponseRole.model_validate(role)

    async def read_role(self, role_id: uuid.UUID) -> ResponseRole | None:
        async with self.db_session as session:
            async with session.begin():
                log.debug(f"Чтение role: {role_id}")
                role_crud = RoleDAL(session)
                role = await role_crud.get(id=role_id)
                if not role:
                    log.error(
                        f"{status.HTTP_404_NOT_FOUND}: Роль не существует {role_id}")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не существет"
                    )
                return ResponseRole(role.id, role.name)

    async def read_roles(self) -> list[ResponseRole] | None:
        async with self.db_session as session:
            async with session.begin():
                log.debug("Чтение всех role")
                role_crud = RoleDAL(session)
                roles = await role_crud.get_all()
                return roles

    async def update_role(self, role_id: uuid.UUID, new_name: str) -> ResponseRole | None:
        async with self.db_session as session:
            async with session.begin():
                log.debug(f"Обнавление role: {role_id}; новое имя: {new_name}")
                role_crud = RoleDAL(session)
                role_exists = await role_crud.get(id=role_id)
                if not role_exists:
                    log.error(
                        f"{status.HTTP_404_NOT_FOUND}: Роль {role_id} не существует")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не существует"
                    )
                update_role_id = await role_crud.update(role_id, name=new_name)
        updated_role = await self.read_role(update_role_id)
        return updated_role

    async def delete_role(self, role_id: uuid.UUID) -> uuid.UUID | None:
        async with self.db_session as session:
            async with session.begin():
                log.debug(f"Удаление role: {role_id}")
                role_crud = RoleDAL(session)
                role_exists = await role_crud.get(id=role_id)
                if not role_exists:
                    log.error(
                        f"{status.HTTP_404_NOT_FOUND}: Роль {role_id} не найден")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не найдена"
                    )
                deleted_role_id = await role_crud.delete(id=role_id)
                return deleted_role_id

    async def get_user_access_area(self, user_id: uuid.UUID) -> ResponseRole | list[ResponseRole]:
        log_msg = f'{user_id=}'
        log.debug(log_msg)
        async with self.db_session as session:
            async with session.begin():
                log_msg = f"Получить область доступа пользователя: {user_id=}"
                log.debug(log_msg)
                role_crud = RoleDAL(session)
                user_crud = UserDAL(session)
                user_exists = await user_crud.get(user_id)
                log_msg = f"{user_id=}, {role_crud=}, {user_crud=}, {user_exists=}"
                log.debug(log_msg)
                if not user_exists:
                    log.error(
                        f"{status.HTTP_404_NOT_FOUND}: Пользователь {user_id} не обнаружен")
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Пользователь не обнаружен"
                    )
                user_roles = await role_crud.get_by_user_id_paginate(user_id=user_id)
                return user_roles

    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db_session as session:
            async with session.begin():
                log.debug(
                    f"Назначение новой роли пользователю {user_id}, role: {role_id}")
                user_role_crud = UserRoleDAL(session)
                user_crud = UserDAL(session)
                role_crud = RoleDAL(session)
                user_exists = await user_crud.get(id=user_id)
                if not user_exists:
                    log_msg = f"{status.HTTP_404_NOT_FOUND}: Пользовательне существует"
                    log.error(log_msg)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Пользователь не существует"
                    )
                role_exists = await role_crud.get(id=role_id)
                if not role_exists:
                    log_msg = f"{status.HTTP_404_NOT_FOUND}: Роль не существует"
                    log.error(log_msg)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не сущeствует"
                    )

                new_user_role = await user_role_crud.create(user_id, role_id)

                return bool(new_user_role)

    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db_session as session:
            async with session.begin():
                log_msg = f"Удаление role {role_id} у пользователя {user_id}"
                log.debug(log_msg)

                user_crud = UserDAL(session)
                role_crud = RoleDAL(session)

                user_exists = await user_crud.get(user_id)
                if not user_exists:
                    log_msg = f"{status.HTTP_404_NOT_FOUND}: Пользователь {user_id} не обнаружен."
                    log.error(log_msg)
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Пользователь не обнаружен"
                    )
                role_exists = await role_crud.get(role_id)
                if not role_exists:
                    lsg_msg = f"{status.HTTP_404_NOT_FOUND}: Роль {role_id} не обнаружен."
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не обнаружена"
                    )
                await role_crud.delete_by_user_id_and_role_id(user_id, role_id)
                return True


@lru_cache
def get_role_service(db_session: AsyncSession = Depends(get_async_session)) -> RoleService:
    log_msg = f'{db_session=}, {get_async_session=}'
    log.debug(log_msg)
    return RoleService(db_session=db_session)
