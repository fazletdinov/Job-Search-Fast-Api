from uuid import UUID
from typing import Union
import logging.config

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from src.database.models import Role, UserRole, User
from src.crud.base_classes import CrudBase
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class RoleDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация RoleDAL")
        self.db_session = session

    async def create(self, name: str) -> Union[Role, Exception]:
        log_message = f'CRUD Создание Role: name={name}'
        log.debug(log_message)
        try:
            new_role = Role(name=name)
            self.db_session.add(new_role)
            await self.db_session.commit()
            return new_role
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при создании Role {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошбика SQLAlchemyError при создании Role")
        except Exception as error:
            log_message = f"Неизвестная ошибка при создании Role {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошбика при создании Role")

    async def delete(self, id: UUID | str) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление Role: id={id}'
        log.debug(log_message)
        try:
            role = await self.db_session.get(Role, id)
            await self.db_session.delete(role)
            await self.db_session.commit()
            return role.id
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении Role {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении Role")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении Role {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении Role")

    async def get(self, id: UUID) -> Union[Role, None, Exception]:
        log_message = f'CRUD Получение Role: id={id}'
        log.debug(log_message)
        try:
            query = select(Role).where(Role.id == id)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получения Role {error}"
            log.exception(log_message)
        except Exception:
            log_message = f"Неизвестная ошибка при получения Role {error}"
            log.exception(log_message)

    async def update(self, id: UUID, **kwargs) -> Union[UUID, Exception, None]:
        log_message = f'CRUD Обновление Role: id={id}'
        log.debug(log_message)
        try:
            query = update(Role).where(Role.id == id).values(
                kwargs).returning(Role.id)
            res = await self.db_session.execute(query)
            role_id_row = res.fetchone()
            await self.db_session.commit()
            if role_id_row is not None:
                return role_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemy при обновление Role {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemy редактирования Role")
        except Exception as error:
            log_message = f"Неизвестная ошибка при обновление Role {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка редактирования Role")

    async def get_by_user_id_paginate(self, user_id: UUID) -> Union[list[Role], Exception, None]:
        log_message = f'CRUD Получение списка Role: user_id={user_id}'
        log.debug(log_message)
        try:
            query = select(Role).join(UserRole, Role.id == UserRole.role_id).\
                join(User, User.id == UserRole.user_id).\
                where(UserRole.user_id == user_id)
            roles = await paginate(self.db_session, query)
            return roles
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Role: {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получения списка Role: {error}"
            log.exception(log_message)

    async def get_by_user_id(self, user_id: UUID) -> Union[list[Role], Exception, None]:
        log_message = f'CRUD Получение списка Role: user_id={user_id}'
        log.debug(log_message)
        try:
            query = select(Role).join(UserRole, Role.id == UserRole.role_id).\
                join(User, User.id == UserRole.user_id).\
                where(UserRole.user_id == user_id)
            res = await self.db_session.execute(query)
            roles = res.fetchall()
            return roles
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Role: {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получения списка Role: {error}"
            log.exception(log_message)

    async def get_by_name(self, name: str) -> Union[Role, None, Exception]:
        log_message = f'CRUD Получение Role: uname={name}'
        log.debug(log_message)
        try:
            query = select(Role).where(Role.name == name)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении Role по name={name}: {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении Role по name={name}: {error}"
            log.exception(log_message)

    async def get_all(self) -> Union[list[Role], None, Exception]:
        log_message = f'CRUD Получение списка Role: all'
        log.debug(log_message)
        try:
            query = select(Role)
            roles = await paginate(self.db_session, query)
            return roles
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Role: all {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении списка Role: all {error}"
            log.exception(log_message)

    async def delete_by_user_id_and_role_id(self,
                                            user_id: UUID,
                                            role_id: UUID) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление Role: user_id: {user_id}; role_id: {role_id}'
        log.debug(log_message)
        try:
            query = select(UserRole).join(Role, Role.id == UserRole.role_id).\
                join(User, User.id == UserRole.user_id).\
                where(UserRole.user_id == user_id,
                      Role.id == role_id)
            res = await self.db_session.execute(query)
            role_rows = res.fetchone()
            if role_rows:
                user_role = await self.db_session.get(UserRole, role_rows[0].id)
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении Role: user_id: {user_id}; role_id: {role_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при попытке удалить Role")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении Role: user_id: {user_id}; role_id: {role_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке удалить Role")
