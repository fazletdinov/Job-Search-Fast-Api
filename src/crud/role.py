from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination.ext.sqlalchemy import paginate

from database.models import Role, UserRole, User
from src.crud.base_classes import CrudBase


class RoleDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create(self, name: str) -> Union[Role, Exception]:
        try:
            new_role = Role(name=name)
            self.db_session.add(new_role)
            await self.db_session.commit()
            return new_role
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошбика при создании Role")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошбика при создании Role")

    async def delete(self, id: UUID | str) -> Union[UUID, None, Exception]:
        try:
            role = await self.db_session.get(Role, id)
            await self.db_session.delete(role)
            await self.db_session.commit()
            return role.id
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при удалении Role")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при удалении Role")

    async def get(self, id: UUID) -> Union[Role, None, Exception]:
        try:
            query = select(Role).where(Role.id == id)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError:
            print("Ошибка получения Role")
        except Exception:
            print("Ошибка получения Role")

    async def update(self, id: UUID, **kwargs) -> Union[UUID, Exception, None]:
        try:
            query = update(Role).where(Role.id == id).values(
                kwargs).returning(Role.id)
            res = await self.db_session.execute(query)
            role_id_row = res.fetchone()
            await self.db_session.commit()
            if role_id_row is not None:
                return role_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка редактирования Role")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка редактирования Role")

    async def get_by_user_id(self, user_id: UUID) -> Union[list[Role], Exception, None]:
        try:
            query = select(Role).join(UserRole, Role.id == UserRole.role_id).\
                join(User, User.id == UserRole.user_id).\
                where(UserRole.user_id == user_id)
            roles = await paginate(self.db_session, query)
            return roles
        except exc.SQLAlchemyError as error:
            print(f"Ошибка получения списка Role: {error}")
        except Exception as error:
            print(f"Ошибка получения списка Role: {error}")

    async def get_by_name(self, name: str) -> Union[Role, None, Exception]:
        try:
            query = select(Role).where(Role.name == name)
            res = await self.db_session.execute(query)
            role_row = res.fetchone()
            if role_row is not None:
                return role_row[0]
        except exc.SQLAlchemyError as error:
            print(f"Ошибка получен Role: {error}")
        except Exception as error:
            print(f"Ошибка получен Role: {error}")

    async def get_all(self) -> Union[list[Role], None, Exception]:
        try:
            query = select(Role)
            roles = await paginate(self.db_session, query)
            return roles
        except exc.SQLAlchemyError as error:
            print(f"Ошибка получения списка Role: {error}")
        except Exception as error:
            print(f"Ошибка получения списка Role: {error}")

    async def delete_by_user_id_and_role_id(self,
                                            user_id: UUID,
                                            role_id: UUID) -> Union[UUID, None, Exception]:
        try:
            query = select(UserRole).join(Role, Role.id == UserRole.role_id).\
                join(User, User.id == UserRole.user_id).\
                where(UserRole.user_id == user_id,
                      Role.id == role_id)
            res = await self.db_session.execute(query)
            role_rows = res.fetchone()
            if role_rows:
                user_role = await self.db_session.get(UserRole, role_rows[0].id)
                await self.db_session.delete(user_role)
                await self.db_session.commit()
                return user_role.id
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при попытке удалить Role")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при попытке удалить Role")
