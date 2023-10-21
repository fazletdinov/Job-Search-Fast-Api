from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from src.users.models import User
from .schema import ResumeRead
from .dals import ResumeDal
from database.session import engine


class CrudResume:

    @staticmethod
    async def _create_resume(body: dict, user: User) -> ResumeRead:
        async with engine.begin() as conn:
            resumedal = ResumeDal(conn)
            resume = await resumedal.create_resume_dal(body,  user=user)
            return resume

    @staticmethod
    async def _get_resume_by_id(resume_id: int, session: AsyncSession) -> ResumeRead:
        async with session.begin():
            resumedal = ResumeDal(session)
            resume = await resumedal.get_resume_by_id_dal(resume_id)
            return resume[0]

    @staticmethod
    async def _get_list_resume(resume_filter, session: AsyncSession):
        async with session.begin():
            resumedal = ResumeDal(session)
            resume = await resumedal.get_list_resume_dal(resume_filter)
            return resume

    @staticmethod
    async def _update_resume(resume_id: int, user: User, kwargs) -> ResumeRead:
        async with engine.begin() as conn:
            resumedal = ResumeDal(conn)
            resume = await resumedal.update_resume_dal(resume_id, user, kwargs)
            return resume

    @staticmethod
    async def _delete_resume(resume_id: int, user: User) -> int:
        async with engine.begin() as conn:
            resumedal = ResumeDal(conn)
            resume = await resumedal.delete_resume_dal(resume_id, user)
            return resume
