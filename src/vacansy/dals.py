from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection
from fastapi_pagination.ext.sqlalchemy import paginate

from src.vacansy.models import Vacansy
from src.users.models import User
from .filter import VacansyFilter

class VacansyDal:

    def __init__(self, session: AsyncConnection | AsyncSession) -> None:
        self.db_session = session

    async def create_vacansy_dal(self, vacansy: dict, user: User):
        query = insert(Vacansy).values(**vacansy, user_id=user.id).returning(Vacansy.id, Vacansy.place_of_work,
                                                                             Vacansy.required_specialt, Vacansy.proposed_salary,
                                                                             Vacansy.working_conditions, Vacansy.required_experience, Vacansy.vacant,
                                                                             Vacansy.created)
        res = await self.db_session.execute(query)
        return res.first()

    async def get_vacansy_by_id_dal(self, vacansy_id: int):
        query = select(Vacansy).where(
            Vacansy.id == vacansy_id, Vacansy.is_active == True)
        res = await self.db_session.execute(query)
        return res.fetchone()

    async def get_list_vacansy_dal(self, vacansy_filter: VacansyFilter):
        query = select(Vacansy.id, Vacansy.place_of_work, Vacansy.required_specialt,
                       Vacansy.proposed_salary, Vacansy.working_conditions, Vacansy.required_experience,
                       Vacansy.vacant, Vacansy.created).where(Vacansy.is_active == True)
        query = vacansy_filter.filter(query)
        query = vacansy_filter.sort(query)
        res = await paginate(self.db_session, query)
 
        return res

    async def update_vacansy_dal(self, vacansy_id: int, body: dict, user: User) -> int:
        query = update(Vacansy).where(Vacansy.id == vacansy_id,
                                      Vacansy.user_id == user.id, Vacansy.is_active == True).values(**body).returning(Vacansy.id)
        res = await self.db_session.execute(query)
        return res.scalar()

    async def delete_vacansy_dal(self, vacansy_id: int, user: User):
        query = delete(Vacansy).where(Vacansy.id == vacansy_id,
                                      Vacansy.user_id == user.id, Vacansy.is_active == True).returning(Vacansy.id)
        res = await self.db_session.execute(query)
        return res.scalar()
