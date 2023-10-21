from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import User
from .schema import VacansyRead
from .dals import VacansyDal
from database.session import engine


class CrudVacansy:
    @staticmethod
    async def _create_vacansy(vacansy: dict, user: User) -> VacansyRead:
        async with engine.begin() as conn:
            vacansydal = VacansyDal(conn)
            vacansy = await vacansydal.create_vacansy_dal(vacansy, user)
            return vacansy

    @staticmethod
    async def _get_vacansy_by_id(vacansy_id: int, session: AsyncSession) -> VacansyRead:
        async with session.begin():
            vacansydal = VacansyDal(session)
            vacansy = await vacansydal.get_vacansy_by_id_dal(vacansy_id)
            return vacansy[0]

    @staticmethod
    async def _update_vacansy(vacansy_id: int, body: dict, user: User) -> int:
        async with engine.begin() as conn: 
            vacansydal = VacansyDal(conn)
            vacansy = await vacansydal.update_vacansy_dal(vacansy_id, body, user)
            return vacansy

    @staticmethod
    async def _delete_vacansy(vacansy_id: int, user: User):
        async with engine.begin() as conn:
            vacansydal = VacansyDal(conn)
            return await vacansydal.delete_vacansy_dal(vacansy_id, user)

    @staticmethod
    async def _get_list_vacansy(vacansy_filter, session: AsyncSession):
        async with session.begin():
            vacansydal = VacansyDal(session)
            vacansy_list = await vacansydal.get_list_vacansy_dal(vacansy_filter)
            return vacansy_list
