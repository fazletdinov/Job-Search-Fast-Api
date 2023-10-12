from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, update, delete

from .models import Resume, User, Vacansy
from .schemas import VacansyCreate


class ResumeDal:
    def __init__(self, session: AsyncSession = None) -> None:
        self.db_sessiom = session

    async def create_resume_dal(self, first_name: str, last_name: str, middle_name: str, age: int, experience: str, education: str, about: str, user: User):
        query = insert(Resume).values(first_name=first_name, last_name=last_name, middle_name=middle_name,
                                      age=age, experience=experience, education=education, about=about,
                                      user_id=user.id).returning(Resume.id, Resume.first_name, Resume.last_name, Resume.middle_name,
                                                                 Resume.age, Resume.experience, Resume.education, Resume.about,
                                                                 Resume.user_id)
        res = await self.db_sessiom.execute(query)
        return res.first()

    async def get_resume_by_id_dal(self, resume_id):
        query = select(Resume).where(Resume.id == resume_id)
        res = await self.db_sessiom.execute(query)
        return res.fetchone()

    async def update_resume_dal(self, resume_id: int, user: User, kwargs: dict):
        query = update(Resume).where(Resume.id == resume_id, Resume.user_id == user.id).values(**kwargs).returning(Resume.id, Resume.first_name, Resume.last_name, Resume.middle_name,
                                                                                                                   Resume.age, Resume.experience, Resume.education, Resume.about,
                                                                                                                   Resume.user_id)
        res = await self.db_sessiom.execute(query)
        return res.first()

    async def delete_resume_dal(self, resume_id: int, user: User) -> int:
        query = delete(Resume).where(Resume.id == resume_id,
                                     Resume.user_id == user.id).returning(Resume.id)
        res = await self.db_sessiom.execute(query)
        return res.scalar()

class VacansyDal:
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create_vacansy_dal(self, vacansy: dict, user: User):
        query = insert(Vacansy).values(**vacansy, user_id=user.id).returning(Vacansy.id, Vacansy.place_of_work,
                                                                            Vacansy.required_specialty, Vacansy.proposed_salary, 
                                                                            Vacansy.working_conditions, Vacansy.required_experience, Vacansy.vacant, 
                                                                            Vacansy.created, Vacansy.is_active, Vacansy.user_id)
        res = await self.db_session.execute(query)
        return res.first()
    
    async def get_vacansy_by_id_dal(self, vacansy_id: int):
        query = select(Vacansy).where(Vacansy.id == vacansy_id)
        res = await self.db_session.execute(query)
        return res.fetchone()
    
    async def update_vacansy_dal(self, vacansy_id: int, body: dict, user: User) -> int:
        query = update(Vacansy).where(Vacansy.id == vacansy_id, Vacansy.user_id == user.id).values(**body).returning(Vacansy.id)
        res = await self.db_session.execute(query)
        return res.scalar()
    
    async def delete_vacansy_dal(self, vacansy_id: int, user: User):
        query = delete(Vacansy).where(Vacansy.id == vacansy_id, Vacansy.user_id == user.id).returning(Vacansy.id)
        res = await self.db_session.execute(query)
        return res.scalar()