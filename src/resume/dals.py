from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from src.resume.models import Resume
from src.users.models import User
from .filter import ResumeFilter


class ResumeDal:
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def  create_resume_dal(self, body: dict, user: User):
        resume: Resume = Resume(**body)
        resume.user = user
        self.db_session.add(resume)
        await self.db_session.commit()
        return resume

    async def get_resume_by_id_dal(self, resume_id: int):
        query = select(Resume).where(Resume.id == resume_id)
        res = await self.db_session.execute(query)
        return res.fetchone()

    async def get_list_resume_dal(self, resume_filter: ResumeFilter):
        query = select(Resume.id, Resume.first_name, Resume.last_name, Resume.middle_name,
                       Resume.age, Resume.experience, Resume.education, Resume.about)
        query = resume_filter.filter(query)
        query = resume_filter.sort(query)
        res = await paginate(self.db_session, query)
        return res

    async def update_resume_dal(self, resume_id: int, user: User, kwargs: dict):
        query = update(Resume).where(Resume.id == resume_id, Resume.user_id == user.id).values(**kwargs).returning(Resume.id, Resume.first_name, Resume.last_name, Resume.middle_name,
                                                                                                                   Resume.age, Resume.experience, Resume.education, Resume.about)
        res = await self.db_session.execute(query)
        await self.db_session.commit()
        return res.first()

    async def delete_resume_dal(self, resume_id: int, user: User) -> int:
        query = delete(Resume).where(Resume.id == resume_id,
                                     Resume.user_id == user.id).returning(Resume.id)
        res = await self.db_session.execute(query)
        await self.db_session.commit()
        return res.scalar()
