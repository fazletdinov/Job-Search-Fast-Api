from uuid import UUID
from typing import Union
import logging.config

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.crud.base_classes import CrudBase
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class UserDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация UserDAL")
        self.db_session = session

    async def create(self, email: str, password: str) -> Union[User, Exception]:
        log_message = f'CRUD Создание User: email={email}'
        log.debug(log_message)
        try:
            new_user = User(
                email=email,
                password=password,
                # roles=["пользователь"]
            )
            self.db_session.add(new_user)
            await self.db_session.commit()
            return new_user
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при создании user - {new_user.__dict__} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создании пользователя")
        except Exception as error:
            log_message = f"Неизвестная ошибка при создании User: email={email} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при создании пользователя")

    async def delete(self, id: UUID | str) -> Union[UUID, Exception, None]:
        log_message = f'CRUD Удаление User: id={id}'
        log.debug(log_message)
        try:
            query = update(User).where(User.id == id, User.is_active == True).\
                values(is_active=False).returning(User.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            user_id_row = res.fetchone()
            if user_id_row is not None:
                return user_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении пользователя {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении пользователя")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении пользователя {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении пользователя")

    async def get(self, id: UUID) -> Union[User, Exception, None]:
        log_message = f'CRUD Получение User: id={id}'
        log.debug(log_message)
        try:
            query = select(User).where(User.id == id, User.is_active == True)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении пользователя: {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении пользователя: {error}"
            log.exception(log_message)

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Обновление User: id={id}'
        log.debug(log_message)
        try:
            query = update(User).where(User.id == id).values(
                kwargs).returning(User.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            user_id_row = res.fetchone()
            if user_id_row is not None:
                return user_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при обновлении User {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении пользователя")
        except Exception as error:
            log_message = f"Неизвестная ошибка при обновлении User {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении пользователя")

    async def get_by_email(self, email: str) -> Union[User, None, Exception]:
        log_message = f'CRUD Получение User: email={email}'
        log.debug(log_message)
        try:
            query = select(User).where(
                User.email == email)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении пользователя по email {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении пользователя по email {error}"
            log.exception(log_message)
