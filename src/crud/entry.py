from uuid import UUID
from typing import Optional

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from database.models import Entry
from src.crud.base_classes import CrudBase


class EntryDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create(self, user_id: UUID, user_agent: str, refresh_token: str) -> Optional[Entry]:
        """Create Entry"""
        new_entry = Entry(
            user_id=user_id,
            user_agent=user_agent
            refresh_token=refresh_token
        )
        try:
            self.db_session.add(new_entry)
            await self.db_session.commit()
            return new_entry
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при создании Entry")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при создании Entry")

    async def delete(self, id: str | UUID) -> Optional[UUID]:
        try:
            query = update(Entry).where(Entry.id == id).values(is_active=False).returning(Entry.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            deleted_entry_id = res.fetchone()
            if deleted_entry_id is not None:
                return deleted_entry_id[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при удалении entry")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при удалении entry")

    async def get(self, id: UUID) -> Optional[Entry]:
        try:
            query = select(Entry).where(Entry.id == id)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при получение Entry")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при получение Entry")
        
    async def update(self, id: UUID, **kwargs) -> Optional[UUID]:
        try:
            query = update(Entry).where(Entry.id == id).values(kwargs).returning(Entry.id)
            res = await self.db_session.execute(query)
            update_entry_id = res.fetchone()
            if update_entry_id is not None:
                return update_entry_id[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при обновлении Entry")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при обновлении Entry")
        
    async def get_by_user_id_list(self,
                                  user_id: UUID,
                                  unique: bool = False,
                                  only_active: bool = False) -> Optional[list[Entry]]
    
        try:
            query = select(Entry).where(Entry.user_id == user_id)
            if only_active:
                query = query.where(Entry.is_active == True)
            if unique:
                query = query.distinct(tuple_(Entry.user_agent, Entry.is_active))
            entries = await paginate(self.db_session, query)
            return entries
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при получении списка Entry")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при получении списка Entry")
    
    async def get_by_user_agent(self,
                                user_agent: str,
                                only_active: bool = False) -> Optional[Entry]:
        try:
            query = select(Entry).where(Entry.user_agent == user_agent):
            if only_active:
                query = query.where(Entry.is_active == True)
            res = await self.db_session.execute(query)
            entry_row = res.fetchone()
            if entry_row is not None:
                return entry_row[0]
        except exc.SQLAlchemyError:
            print("Ошибка при получении Entry")
        except Exception:
            print("Ошибка при получении Entry")