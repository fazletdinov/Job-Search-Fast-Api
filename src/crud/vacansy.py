from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from database.models import Vacansy
from src.crud.base_classes import CrudBase
from src.utils.filter import VacansyFilter


class VacansyDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create(self, vacansy: dict, hr_id: UUID) -> Union[Vacansy, Exception]:
        try:
            vacansy: Vacansy = Vacansy(hr_id=hr_id, **vacansy)
            self.db_session.add(vacansy)
            await self.db_session.commit()
            return vacansy
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создании вакансии")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при создании вакансии")

    async def get(self, vacansy_id: UUID) -> Union[Vacansy, None, Exception]:
        try:
            query = select(Vacansy).options(selectinload(Vacansy.comments)).where(
                Vacansy.id == vacansy_id, Vacansy.is_active == True)
            res = await self.db_session.execute(query)
            vacansy_row = res.fetchone()
            if vacansy_row is not None:
                return vacansy_row[0]
        except exc.SQLAlchemyError as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Ошибка SQLAlchemyError при получении Vacansy: {error}")
        except Exception as error:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Неизвестная ошибка при получении Vacansy: {error}")

    async def get_list_vacansy_dal(self, vacansy_filter: VacansyFilter) -> Union[list[Vacansy], None, Exception]:
        try:
            query = select(Vacansy.id, Vacansy.place_of_work, Vacansy.required_specialt,
                           Vacansy.proposed_salary, Vacansy.working_conditions, Vacansy.required_experience,
                           Vacansy.created).where(Vacansy.is_active == True)
            query = vacansy_filter.filter(query)
            query = vacansy_filter.sort(query)
            vacansy_rows = await paginate(self.db_session, query)
            return vacansy_rows
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при получении списка Vacansy")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении списка Vacansy")

    async def update(self, vacansy_id: UUID, hr_id: UUID, body: dict) -> Union[UUID, None, Exception]:
        try:
            query = update(Vacansy).where(Vacansy.id == vacansy_id, Vacansy.is_active == True,
                                          Vacansy.hr_id == hr_id).values(**body).returning(Vacansy.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            vacansy_row = res.fetchone()
            if vacansy_row is not None:
                return vacansy_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Vacansy")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении Vacansy")

    async def delete(self, vacansy_id: UUID, hr_id: UUID) -> Union[UUID, None, Exception]:
        try:
            query = delete(Vacansy).where(Vacansy.id == vacansy_id, Vacansy.is_active == True,
                                          Vacansy.hr_id == hr_id).returning(Vacansy.id)

            res = await self.db_session.execute(query)
            await self.db_session.commit()
            return res.scalar()
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при попытке удалить Vacansy")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке удалить Vacansy")

    async def get_by_hr_id(self, hr_id: UUID) -> Union[list[Vacansy], None, Exception]:
        try:
            query = select(Vacansy).where(Vacansy.hr_id ==
                                          hr_id, Vacansy.is_active == True)
            vacansy_rows = await paginate(self.db_session, query)
            return vacansy_rows
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при получение списка Vacansy по hr_id")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении списка Vacansy по hr_id")
