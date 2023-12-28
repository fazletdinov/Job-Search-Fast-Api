from uuid import UUID
from typing import Union
import logging.config

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import UserRole
from src.crud.base_classes import CrudBase
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class UserRoleDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация UserRoleDAL")
        self.db_session = session

    async def create(self, user_id: UUID, role_id: UUID) -> Union[UserRole, Exception]:
        log_message = f'CRUD Создание UserRole: user_id={user_id}'
        log.debug(log_message)
        try:
            new_user_role = UserRole(user_id=user_id,
                                     role_id=role_id)
            self.db_session.add(new_user_role)
            await self.db_session.commit()
            return new_user_role
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при создании UserRole: user_id: {user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создание UserRole")
        except Exception as error:
            log_message = f"Неизвестная ошибка при создании UserRole: user_id: {user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при создании UserRole")

    async def delete(self, id: UUID) -> Union[UUID, Exception, None]:
        log_message = f'CRUD Удаление UserRole: id={id}'
        log.debug(log_message)
        try:
            user_role = await self.db_session.get(UserRole, id)
            if user_role is not None:
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemy при удалении UserRole: id={id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении UserRole")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении UserRole: id={id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении UserRole")

    async def delete_by_user_id(self, user_id: str | UUID) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление UserRole: user_id={user_id}'
        log.debug(log_message)
        try:
            user_role = await self.db_session.get(UserRole, user_id)
            if user_role is not None:
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении UserRole: user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении UserRole по user_id")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении UserRole: user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении UserRole по user_id")

    async def delete_by_role_id(self, role_id: UUID | str) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление UserRole: role_id={role_id}'
        log.debug(log_message)
        try:
            user_role = await self.db_session.get(UserRole, role_id)
            if user_role is not None:
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении UserRole: role_id={role_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении UserRole по role_id")
        except Exception:
            log_message = f"Неизвестная ошибка при удалении UserRole: role_id={role_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении UserRole по role_id")

    async def get(self, id: UUID) -> Union[UserRole, None, Exception]:
        log_message = f'CRUD Получение UserRole: id={id}'
        log.debug(log_message)
        try:
            query = select(UserRole).where(UserRole.id == id)
            res = await self.db_session.execute(query)
            user_role = res.fetchone()
            if user_role is not None:
                return user_role[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении UserRole: id={id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении UserRole: id={id} {error}"
            log.exception(log_message)

    async def get_by_user_id(self, user_id: UUID) -> Union[list[UserRole], None, Exception]:
        log_message = f'CRUD Получение списка UserRole: user_id={user_id}'
        log.debug(log_message)
        try:
            query = select(UserRole).where(UserRole.user_id == user_id)
            res = await self.db_session.execute(query)
            user_role_rows = res.fetchall()
            if user_role_rows is not None:
                return [row[0] for row in user_role_rows]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка UserRole: user_id={user_id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении списка UserRole: user_id={user_id} {error}"
            log.exception(log_message)

    async def get_by_role_id(self, role_id: UUID) -> Union[list[UserRole], None, Exception]:
        log_message = f'CRUD Получение списка UserRole: role_id={role_id}'
        log.debug(log_message)
        try:
            query = select(UserRole).where(UserRole.role_id == role_id)
            res = await self.db_session.execute(query)
            user_role_rows = res.fetchall()
            if user_role_rows is not None:
                return [row[0] for row in user_role_rows]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка UserRole: role_id={role_id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении списка UserRole: role_id={role_id} {error}"
            log.exception(log_message)

    async def update(self, id: UUID, **kwargs) -> Union[UUID, Exception, None]:
        log_message = f'CRUD Обновление UserRole: id={id}'
        log.debug(log_message)
        try:
            query = update(UserRole).where(UserRole.id == id).values(
                kwargs).returning(UserRole.id)
            res = await self.db_session.execute(query)
            user_role_id = res.fetchone()
            await self.db_session.commit()
            if user_role_id is not None:
                return user_role_id[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при обновлении UserRole: id={id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении UserRole")
        except Exception as error:
            log_message = f"Неизвестная ошибка при обновлении UserRole: id={id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении UserRole")
