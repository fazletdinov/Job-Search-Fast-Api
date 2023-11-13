from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from database.models import Resume
from src.crud.base_classes import CrudBase
from src.utils.filter import ResumeFilter


class ResumeDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create(self, body: dict, user_id: UUID) -> Union[Resume, None, Exception]:
        try:
            resume: Resume = Resume(user_id=user_id, **body)
            self.db_session.add(resume)
            await self.db_session.commit()
            return resume
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при попытке создать Resume")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке создать Resume")

    async def get(self, resume_id: UUID) -> Union[Resume, None, Exception]:
        try:
            query = select(Resume).where(Resume.id == resume_id)
            res = await self.db_session.execute(query)
            resume_row = res.fetchone()
            if resume_row is not None:
                return resume_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при получении Resume")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении Resume")

    async def get_list_resume(self, resume_filter: ResumeFilter) -> Union[list[Resume], None, Exception]:
        try:
            query = select(Resume.id, Resume.first_name, Resume.last_name, Resume.middle_name,
                           Resume.age, Resume.experience, Resume.education, Resume.about)
            query = resume_filter.filter(query)
            query = resume_filter.sort(query)
            resume_rows = await paginate(self.db_session, query)
            return resume_rows
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при получении списка Resume")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении списка Resume")

    async def update(self, resume_id: int, user_id: UUID, kwargs: dict) -> Union[UUID, None, Exception]:
        try:
            query = update(Resume).where(Resume.id == resume_id, Resume.user_id == user_id).values(
                **kwargs).returning(Resume.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            resume_row = res.fetchone()
            if resume_row is not None:
                return resume_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Resume")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении Resume")

    async def delete(self, resume_id: int, user_id: UUID) -> Union[UUID, None, Exception]:
        try:
            query = delete(Resume).where(Resume.id == resume_id,
                                         Resume.user_id == user_id).returning(Resume.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            resume_id_row = res.fetchone()
            if resume_id_row is not None:
                return resume_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ощибка SQLAlchemyError при удалении Resume")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении Resume")

    async def get_by_user_id(self, user_id: UUID) -> Union[list[Resume], None, Exception]:
        try:
            query = select(Resume).where(Resume.user_id == user_id)
            res = await self.db_session.execute(query)
            resume_rows = res.fetchone()
            if resume_rows is not None:
                return resume_rows[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при получение списка Resume по user_id")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении списка Resume с помощью user_id")