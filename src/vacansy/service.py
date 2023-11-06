from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from .schema import VacansyReadAfterPost
from .dals import VacansyDal, CommentDal
from database.session import engine


class CrudVacansy:
    @staticmethod
    async def _create_vacansy(vacansy: dict, user: User, session: AsyncSession) -> VacansyReadAfterPost:
        vacansydal = VacansyDal(session)
        vacansy = await vacansydal.create_vacansy_dal(vacansy, user)
        return vacansy

    @staticmethod
    async def _get_vacansy_by_id(vacansy_id: int, session: AsyncSession):
        async with session.begin():
            vacansydal = VacansyDal(session)
            vacansy = await vacansydal.get_vacansy_by_id_dal(vacansy_id)
            if vacansy is not None:
                return vacansy[0]
            return vacansy

    @staticmethod
    async def _update_vacansy(vacansy_id: int, body: dict, user: User, session: AsyncSession):
        vacansydal = VacansyDal(session)
        vacansy = await vacansydal.update_vacansy_dal(vacansy_id, body, user)
        return vacansy

    @staticmethod
    async def _delete_vacansy(vacansy_id: int, user: User, session: AsyncSession):
        vacansydal = VacansyDal(session)
        return await vacansydal.delete_vacansy_dal(vacansy_id, user)
    
    @staticmethod
    async def _admin_delete_vacansy(vacansy_id: int, user: User, session: AsyncSession):
        vacansydal = VacansyDal(session)
        return await vacansydal.admin_delete_vacansy_dal(vacansy_id, user)

    @staticmethod
    async def _get_list_vacansy(vacansy_filter, session: AsyncSession):
        async with session.begin():
            vacansydal = VacansyDal(session)
            vacansy_list = await vacansydal.get_list_vacansy_dal(vacansy_filter)
            return vacansy_list


class CrudComment:

    @staticmethod
    async def _create_comment(vacansy_id: int, comment: dict, user: User, session: AsyncSession):
        commentdal = CommentDal(session)
        comment = await commentdal.create_comment_dal(vacansy_id, comment, user)
        return comment

    @staticmethod
    async def _get_list_comments(vacansy_id: int, session: AsyncSession):
        async with session.begin():
            commentdal = CommentDal(session)
            comments = await commentdal.get_list_comments_dal(vacansy_id)
            return comments

    @staticmethod
    async def _delete_comment(vacansy_id: int, comment_id: int, user: User, session: AsyncSession):
        commentdal = CommentDal(session)
        comment = await commentdal.delete_comment_dal(vacansy_id, comment_id, user)
        return comment
    
    @staticmethod
    async def _admin_delete_comment(vacansy_id: int, comment_id: int, user: User, session: AsyncSession):
        commentdal = CommentDal(session)
        comment = await commentdal.admin_delete_comment_dal(vacansy_id, comment_id, user)
        return comment

    @staticmethod
    async def _update_comment(vacansy_id: int, comment_id: int, comment: dict, user: User, session: AsyncSession):
        commentdal = CommentDal(session)
        comment = await commentdal.update_comment_dal(vacansy_id, comment_id, comment, user)
        return comment
