from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import aliased, selectinload

from src.vacansy.models import Vacansy, Comment
from src.users.models import User
from .filter import VacansyFilter

class VacansyDal:

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create_vacansy_dal(self, vacansy: dict, user: User):
        vacansy: Vacansy = Vacansy(**vacansy)
        vacansy.user = user
        self.db_session.add(vacansy)
        await self.db_session.commit()
        return vacansy

    async def get_vacansy_by_id_dal(self, vacansy_id: int):
        query = select(Vacansy).options(selectinload(Vacansy.comments)).where(
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
        await self.db_session.commit()
        return res.scalar()

    async def delete_vacansy_dal(self, vacansy_id: int, user: User):
        query = delete(Vacansy).where(Vacansy.id == vacansy_id,
                                      Vacansy.user_id == user.id, Vacansy.is_active == True).returning(Vacansy.id)

        res = await self.db_session.execute(query)
        await self.db_session.commit()
        return res.scalar()


class CommentDal:

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create_comment_dal(self, vacansy_id: int, comment: dict, user: User):
        vacansys = await self.db_session.get(Vacansy, vacansy_id)
        comm: Comment = Comment(**comment)
        comm.vacansy = vacansys
        comm.owner = user
        self.db_session.add(comm)
        await self.db_session.commit()
        return comm
    
    async def get_list_comments_dal(self, vacansy_id: int):
        query = select(Comment.id, Comment.text, Comment.created).where(Comment.vacansy_id == vacansy_id)
        res = await self.db_session.execute(query)
        return res.fetchall()
    
    async def delete_comment_dal(self, vacansy_id: int, comment_id: int, user: User):
        query = delete(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id == comment_id, Comment.user_id == user.id).returning(Comment.id)
        res = await self.db_session.execute(query)
        await self.db_session.commit()
        return res.scalar()
    
    async def update_comment_dal(self, vacansy_id: int, comment_id: int, comment: dict, user: User):
        query = update(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id == comment_id,
                                      Comment.user_id == user.id).values(**comment).returning(Comment.id)
        res = await self.db_session.execute(query)
        await self.db_session.commit()
        return res.scalar()
    
