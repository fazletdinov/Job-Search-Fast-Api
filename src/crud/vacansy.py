from uuid import UUID
from typing import Union
import logging.config

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from src.database.models import Vacansy
from src.crud.base_classes import CrudBase
from src.utils.filter import VacansyFilter
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class VacansyDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация VacansyDAL")
        self.db_session = session

    async def create(self, vacansy: dict, hr_id: UUID) -> Union[Vacansy, Exception]:
        log_message = f'CRUD Создание Vacansy: vacansy={vacansy}, hr_id={hr_id}'
        log.debug(log_message)
        try:
            vacansy: Vacansy = Vacansy(hr_id=hr_id, **vacansy)
            self.db_session.add(vacansy)
            await self.db_session.commit()
            return vacansy
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при создании Vacansy: vacansy={vacansy}, hr_id={hr_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создании вакансии")
        except Exception as error:
            log_message = f"Неизвестная ошибка при создании Vacansy: vacansy={vacansy}, hr_id={hr_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при создании вакансии")

    async def get(self, vacansy_id: UUID) -> Union[Vacansy, None, Exception]:
        log_message = f'CRUD Получение Vacansy: vacansy_id={vacansy_id}'
        log.debug(log_message)
        try:
            query = select(Vacansy).options(selectinload(Vacansy.comments)).where(
                Vacansy.id == vacansy_id, Vacansy.is_active == True)
            res = await self.db_session.execute(query)
            vacansy_row = res.fetchone()
            if vacansy_row is not None:
                return vacansy_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении Vacansy: vacansy_id={vacansy_id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении Vacansy: vacansy_id={vacansy_id} {error}"
            log.exception(log_message)

    async def get_list_vacansy_dal(self, vacansy_filter: VacansyFilter) -> Union[list[Vacansy], None, Exception]:
        log_message = f'CRUD Получение списка Vacansy: vacansy_filter={vacansy_filter}'
        log.debug(log_message)
        try:
            query = select(Vacansy.id, Vacansy.place_of_work, Vacansy.required_specialt,
                           Vacansy.proposed_salary, Vacansy.working_conditions, Vacansy.required_experience,
                           Vacansy.created).where(Vacansy.is_active == True)
            query = vacansy_filter.filter(query)
            query = vacansy_filter.sort(query)
            vacansy_rows = await paginate(self.db_session, query)
            return vacansy_rows
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Vacansy: vacansy_filter={vacansy_filter} {error}"
            log.exception(log_message)
        except Exception:
            log_message = f"Неизвестная ошибка при получении списка Vacansy: vacansy_filter={vacansy_filter} {error}"
            log.exception(log_message)

    async def update(self, vacansy_id: UUID, hr_id: UUID, body: dict) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Обновление Vacansy: vacansy_id={vacansy_id}, hr_id={hr_id}, body={body}'
        log.debug(log_message)
        try:
            query = update(Vacansy).where(Vacansy.id == vacansy_id, Vacansy.is_active == True,
                                          Vacansy.hr_id == hr_id).values(**body).returning(Vacansy.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            vacansy_row = res.fetchone()
            if vacansy_row is not None:
                return vacansy_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при обновлении Vacansy: vacansy_id={vacansy_id}, hr_id={hr_id}, body={body} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Vacansy")
        except Exception as error:
            log_message = f"Неизвестная ошибка при обновлени Vacansy: vacansy_id={vacansy_id}, hr_id={hr_id}, body={body} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении Vacansy")

    async def delete(self, vacansy_id: UUID, hr_id: UUID) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление Vacansy: vacansy_id={vacansy_id}, hr_id={hr_id}'
        log.debug(log_message)
        try:
            query = delete(Vacansy).where(Vacansy.id == vacansy_id, Vacansy.is_active == True,
                                          Vacansy.hr_id == hr_id).returning(Vacansy.id)

            res = await self.db_session.execute(query)
            await self.db_session.commit()
            return res.scalar()
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении Vacansy: vacansy_id={vacansy_id}, hr_id={hr_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при попытке удалить Vacansy")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении Vacansy: vacansy_id={vacansy_id}, hr_id={hr_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке удалить Vacansy")

    async def get_by_hr_id(self, hr_id: UUID) -> Union[list[Vacansy], None, Exception]:
        log_message = f'CRUD Получение списка Vacansy: hr_id={hr_id}'
        log.debug(log_message)
        try:
            query = select(Vacansy).where(Vacansy.hr_id ==
                                          hr_id, Vacansy.is_active == True)
            vacansy_rows = await paginate(self.db_session, query)
            return vacansy_rows
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Vacansy: hr_id={hr_id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении списка Vacansy: hr_id={hr_id} {error}"
            log.exception(log_message)
