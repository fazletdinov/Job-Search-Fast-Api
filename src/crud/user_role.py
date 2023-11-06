from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import UserRole
from src.crud.base_classes import CrudBase


class UserRoleDAL(CrudBase):
    
    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session


    async def create(self, user_id: UUID, role_id: UUID) -> Union[UserRole, Exception]:
        try:
            new_user_role = UserRole(user_id=user_id,
                                     role_id=role_id)
            self.db_session.add(new_user_role)
            await self.db_session.commit()
            return new_user_role
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создание UserRole")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при создании UserRole")
    
    async def delete(self, id: UUID) -> Union[UUID, Exception, None]:
        try:
            user_role = await self.db_session.get(UserRole, id)
            if user_role is not None:
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении UserRole")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении UserRole")
    
    async def delete_by_user_id(self, user_id: str | UUID) -> Union[UUID, None, Exception]:
        try:
            user_role = await self.db_session.get(UserRole, user_id)
            if user_role is not None:
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении UserRole по user_id")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении UserRole по user_id")

    async def delete_by_role_id(self, role_id: UUID | str ) -> Union[UUID, None, Exception]:
        try:
            user_role = await self.db_session.get(UserRole, role_id)
            if user_role is not None:
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении UserRole по role_id")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении UserRole по role_id")
        
    async def get(self, id: UUID) -> Union[UserRole, None, Exception]:
        try:
            query = select(UserRole).where(UserRole.id == id)
            res = await self.db_session.execute(query)
            user_role = res.fetchone()
            if user_role is not None:
                return user_role[0]
        except exc.SQLAlchemyError as error:
            print(f"Ошибка SQLAlchemyError при получении UserRole: {error}")
        except Exception as error:
            print(f"Неизвестна ошибка при получении UserRole: {error}")

    async def get_by_user_id(self, user_id: UUID) -> Union[list[UserRole], None, Exception]:
        try:
            query = select(UserRole).where(UserRole.user_id == user_id)
            res = await self.db_session.execute(query)
            user_role_rows = res.fetchall()
            if user_role_rows is not None:
                return [row[0] for row in user_role_rows]
        except exc.SQLAlchemyError as error:
            print(f"Ошибка SQLAlchemyError при получении списка UserRole по user_id: {error}")
        except Exception as error:
            print(f"Неизвестная ошибка при получении списка UserRole по user_id: {error}")
    
    async def get_by_role_id(self, role_id: UUID) -> Union[list[UserRole], None, Exception]:
        try:
            query = select(UserRole).where(UserRole.role_id == role_id)
            res = await self.db_session.execute(query)
            user_role_rows = res.fetchall()
            if user_role_rows is not None:
                return [row[0] for row in user_role_rows]
        except exc.SQLAlchemyError as error:
            print(f"Ошибка SQLAlchemyError при получении списка UserRole по role_id: {error}")
        except Exception as error:
            print(f"Неизвестная ошибка при получении списка UserRole по role_id: {error}")

    async def update(self, id: UUID, **kwargs) -> Union[UUID, Exception, None]:
        try:
            query = update(UserRole).where(UserRole.id == id).values(kwargs).returning(UserRole.id)
            res = await self.db_session.execute(query)
            user_role_id = res.fetchone()
            await self.db_session.commit()
            if user_role_id is not None:
                return user_role_id[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении UserRole")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении UserRole")
        