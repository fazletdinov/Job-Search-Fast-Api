import logging
import uuid
from abc import ABC, abstractmethod
from functools import lru_cache
from typing import List, Optional

from fastapi import status, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from crud.role import RoleDAL
from crud.user_role import UserRoleDAL
from crud.user import UserDAL
from database.session import get_async_session
from schemas.role import RoleResponse


class RoleServiceBase(ABC):

    @abstractmethod
    async def create_role(self, role_name: str) -> Optional[RoleResponse]:
        """Создание новой роли"""

    @abstractmethod
    async def read_role(self, role_id: uuid.UUID) -> Optional[RoleResponse]:
        """Чтение роли из БД"""

    @abstractmethod
    async def read_roles(self) -> Optional[list[RoleResponse]]:
        """Получение списка ролей"""

    @abstractmethod
    async def update_role(self, role_id: uuid.UUID, new_name: str) -> Optional[RoleResponse]:
        """Обновление роли"""

    @abstractmethod
    async def delete_role(self, role_id: uuid.UUID) -> uuid.UUID | None:
        """Удаление роли"""

    @abstractmethod
    async def get_user_access_area(self, user_id: uuid.UUID) -> RoleResponse | list[RoleResponse]:
        """Получить область доступа для пользователя по его идентификатору"""
    
    @abstractmethod
    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Установите новую или дополнительную роль для пользователя"""

    @abstractmethod
    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Удалить роль из ролей пользователей"""


class RoleService(RoleServiceBase):
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_role(self, role_name: str) -> RoleResponse | None:
        async with self.db_session as session: 
            async with session.begin():
                role_crud = RoleDAL(session)
                role_exists = await role_crud.get_by_name(role_name)
                if role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Эта роль существует"
                    )
                role = await role_crud.create(name=role_name)
                return RoleResponse(role.id, role.name)

    async def read_role(self, role_id: uuid.UUID) -> RoleResponse | None:
        async with self.db_session as session:
            async with session.begin():
                role_crud = RoleDAL(session)
                role = await role_crud.get(id=role_id)
                if not role:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не существет"
                    )
                return RoleResponse(role.id, role.name)

    async def read_roles(self) -> list[RoleResponse] | None:
        async with self.db_session as session:
            async with session.begin():
                role_crud = RoleDAL(session)
                roles = await role_crud.get_all()
                return roles

    async def update_role(self, role_id: uuid.UUID, new_name: str) -> RoleResponse | None:
        async with self.db_session as session:
            async with session.begin():
                role_crud = RoleDAL(session)
                role_exists = await role_crud.get(id=role_id)
                if not role_exists:
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
                role_crud = RoleDAL(session)
                role_exists = await role_crud.get(id=role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не найдена"
                    )
                deleted_role_id = await role_crud.delete(id=role_id)
                return deleted_role_id
    
    async def get_user_access_area(self, user_id: uuid.UUID) -> RoleResponse | list[RoleResponse]:
        async with self.db_session as session:
            async with session.begin():
                role_crud = RoleDAL(session)
                user_crud = UserDAL(session)
                user_exists = await user_crud.get(user_id)
                if not user_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Пользователь не обнаружен"
                    )
                user_roles = await role_crud.get_by_user_id_paginate(user_id=user_id)
                return user_roles
            
    async def set_role_to_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db_session as session:
            async with session.begin():
                user_role_crud = UserRoleDAL(session)
                user_crud = UserDAL(session)
                role_crud = RoleDAL(session)
                user_exists = await user_crud.get(id=user_id)
                if not user_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Пользователь не существует"
                    )
                role_exists = await role_crud.get(id=role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не суещствует"
                    )
                
                new_user_role = await user_role_crud.create(user_id, role_id)
                return bool(new_user_role)
    
    async def remove_role_from_user(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        async with self.db_session as session:
            async with session.begin():
                user_crud = UserDAL(session)
                role_crud = RoleDAL(session)

                user_exists = await user_crud.get(user_id)
                if not user_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Пользователь не обнаружен"
                    )
                role_exists = await role_crud.get(role_id)
                if not role_exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Роль не обнаружена"
                    )
                await role_crud.delete_by_user_id_and_role_id(user_id, role_id)
                return True

@lru_cache
def get_role_service(db_session: AsyncSession = Depends(get_async_session)) -> RoleService:
    return RoleService(db_session=db_session)
        