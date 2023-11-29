from uuid import UUID
from typing import Optional
import logging
import logging.config

from fastapi import status, HTTPException
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, update, exc, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Entry
from src.crud.base_classes import CrudBase
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class EntryDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация EntryDAL")
        self.db_session = session

    async def create(self, user_id: UUID, user_agent: str, refresh_token: str) -> Optional[Entry]:
        """Create Entry"""
        log_message = f'CRUD Создание Entry: user_id={user_id}, user_agent={user_agent}, refresh_token={refresh_token}'
        log.debug(log_message)

        new_entry = Entry(
            user_id=user_id,
            user_agent=user_agent,
            refresh_token=refresh_token
        )
        try:
            self.db_session.add(new_entry)
            await self.db_session.commit()
            return new_entry
        except exc.SQLAlchemyError as error:
            log_message = f'Ошибка SQLAlchemyError при создании Entry: {new_entry.__dict__}'
            log.error(log_message)
            log.exception(error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создании Entry")
        except Exception as error:
            log_message = f'Неизвестная ошибка при создании Entry: {new_entry.__dict__}'
            log.error(log_message)
            log.exception(error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при создании Entry")

    async def delete(self, id: str | UUID) -> Optional[UUID]:
        log_message = f'CRUD Удаление Entry: id={id}'
        log.debug(log_message)
        try:
            query = update(Entry).where(Entry.id == id).values(
                is_active=False).returning(Entry.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            deleted_entry_id = res.fetchone()
            if deleted_entry_id is not None:
                return deleted_entry_id[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении Entry"
            log.error(log_message)
            log.exception(error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении entry")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении Entry"
            log.error(log_message)
            log.exception(error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении entry")

    async def get(self, id: UUID) -> Optional[Entry]:
        log_message = f'CRUD Получение Entry: id={id}'
        log.debug(log_message)
        try:
            query = select(Entry).where(Entry.id == id)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f'Ошибка SQLAlchemyError при получении Entry: id={id}'
            log.error(log_message)
            log.exception(error)

        except Exception as error:
            log_message = f'Неизвестная ошибка при получении Entry: id={id}'
            log.error(log_message)
            log.exception(error)

    async def update(self, id: UUID, **kwargs) -> Optional[UUID]:
        log_message = f'CRUD Обновление Entry: id={id}'
        log.debug(log_message)
        try:
            query = update(Entry).where(Entry.id == id).values(
                kwargs).returning(Entry.id)
            res = await self.db_session.execute(query)
            update_entry_id = res.fetchone()
            if update_entry_id is not None:
                return update_entry_id[0]
        except exc.SQLAlchemyError as error:
            log_message = "Ощибка SQLAlchemyError при обновлении Entry"
            log.error(log_message)
            log.exception(error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Entry")
        except Exception as error:
            log_message = "Неизвестная ошибка при обновлении Entry"
            log.error(log_message)
            log.exception(error)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении Entry")

    async def get_by_user_id_list(self,
                                  user_id: UUID,
                                  unique: bool = False,
                                  only_active: bool = False) -> Optional[list[Entry]]:
        log_message = f'CRUD Получение списка Entry: user_id = {user_id}'
        log.debug(log_message)

        try:
            query = select(Entry).where(Entry.user_id == user_id)
            if only_active:
                query = query.where(Entry.is_active == True)
            if unique:
                query = query.distinct(
                    tuple_(Entry.user_agent, Entry.is_active))
            entries = await paginate(self.db_session, query)
            return entries
        except exc.SQLAlchemyError as error:
            log_message = f"Ощибка SQLAlchemyError при получении списка Entry по user_id = {user_id}"
            log.error(log_message)
            log.exception(error)
        except Exception as error:
            log_message = f"Неизвестная ощибка при получении списка Entry по user_id = {user_id}"
            log.error(log_message)
            log.exception(error)

    async def get_by_user_agent(self,
                                user_agent: str,
                                only_active: bool = False) -> Optional[Entry]:
        log_message = f'CRUD Получение списка Entry: user_agent = {user_agent}'
        log.debug(log_message)
        try:
            query = select(Entry).where(Entry.user_agent == user_agent)
            if only_active:
                query = query.where(Entry.is_active == True)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ощибка SQLAlchemyError при получении списка Entry по user_agent = {user_agent}"
            log.error(log_message)
            log.exception(error)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении списка Entry по user_agent = {user_agent}"
            log.error(log_message)
            log.exception(error)
