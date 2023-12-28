from uuid import UUID
from typing import Union
import logging.config

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from src.database.models import Resume
from src.crud.base_classes import CrudBase
from src.utils.filter import ResumeFilter
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class ResumeDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация ResumeDAL")
        self.db_session = session

    async def create(self, body: dict, user_id: UUID) -> Union[Resume, None, Exception]:
        log_message = f'CRUD Создание Resume: body={body}; user_id={user_id}'
        log.debug(log_message)
        try:
            resume: Resume = Resume(user_id=user_id, **body)
            self.db_session.add(resume)
            await self.db_session.commit()
            return resume
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при создании Resume: body={body}; user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при попытке создать Resume")
        except Exception:
            log_message = f"Неизвестная ошибка при создании Resume: body={body}; user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке создать Resume")

    async def get(self, resume_id: UUID) -> Union[Resume, None, Exception]:
        log_message = f'CRUD Получение Resume: resume_id={resume_id}'
        log.debug(log_message)
        try:
            query = select(Resume).where(Resume.id == resume_id)
            res = await self.db_session.execute(query)
            resume_row = res.fetchone()
            if resume_row is not None:
                return resume_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении Resume: resume_id={resume_id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"Неизвестная ошибка при получени Resume: resume_id={resume_id} {error}"
            log.exception(log_message)

    async def get_list_resume(self, resume_filter: ResumeFilter) -> Union[list[Resume], None, Exception]:
        log_message = f'CRUD Получение списка Resume: resume_filter={resume_filter}'
        log.debug(log_message)
        try:
            query = select(Resume.id, Resume.first_name, Resume.last_name, Resume.middle_name,
                           Resume.age, Resume.experience, Resume.education, Resume.about)
            query = resume_filter.filter(query)
            query = resume_filter.sort(query)
            resume_rows = await paginate(self.db_session, query)
            return resume_rows
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Resume: resume_filter={resume_filter} {error}"
            log.exception(log_message)
        except Exception:
            log_message = f"Неизвестная ошибка при получении списка Resume: resume_filter={resume_filter} {error}"
            log.exception(log_message)

    async def update(self, resume_id: int, user_id: UUID, kwargs: dict) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Обновление Resume: resume_id={resume_id}, user_id={user_id}, kwargs={kwargs}'
        log.debug(log_message)
        try:
            query = update(Resume).where(Resume.id == resume_id, Resume.user_id == user_id).values(
                **kwargs).returning(Resume.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            resume_row = res.fetchone()
            if resume_row is not None:
                return resume_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при обновлении Resume: resume_id={resume_id}, user_id={user_id}, kwargs={kwargs} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Resume")
        except Exception:
            log_message = f"Неизвестная ошибка при обновлении Resume: resume_id={resume_id}, user_id={user_id}, kwargs={kwargs} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении Resume")

    async def delete(self, resume_id: int, user_id: UUID) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление Resume: resume_id={resume_id}, user_id={user_id}'
        log.debug(log_message)
        try:
            query = delete(Resume).where(Resume.id == resume_id,
                                         Resume.user_id == user_id).returning(Resume.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            resume_id_row = res.fetchone()
            if resume_id_row is not None:
                return resume_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении Resume: resume_id={resume_id}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ощибка SQLAlchemyError при удалении Resume")
        except Exception:
            log_message = f"Неизвестная ошибка при удалении Resume: resume_id={resume_id}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении Resume")

    async def get_by_user_id(self, user_id: UUID) -> Union[list[Resume], None, Exception]:
        log_message = f'CRUD Получении списка Resume: user_id={user_id}'
        log.debug(log_message)
        try:
            query = select(Resume).where(Resume.user_id == user_id)
            res = await self.db_session.execute(query)
            resume_rows = res.fetchone()
            if resume_rows is not None:
                return resume_rows[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении списка Resume: user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при получение списка Resume по user_id")
        except Exception as error:
            log_message = f"Неизвестная ошибка при получении списка Resume: user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении списка Resume с помощью user_id")
