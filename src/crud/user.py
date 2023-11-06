from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from src.crud.base_classes import CrudBase


class UserDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create(self, email: str, password: str) -> Union[User, Exception]:
        try:
            new_user = User(
                email=email,
                password=password
            )
            self.db_session.add(new_user)
            await self.db_session.commit()
            return new_user
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при создании пользователя")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при создании пользователя")

    async def delete(self, id: UUID | str) -> Union[UUID, Exception, None]:
        try:
            query = update(User).where(User.id == id, User.is_active == True).\
                values(is_active=False).returning(User.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            user_id_row = res.fetchone()
            if user_id_row is not None:
                return user_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при удалении пользователя")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при удалении пользователя")

    async def get(self, id: UUID) -> Union[User, Exception, None]:
        try:
            query = select(User).where(User.id == id, User.is_active == True)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as error:
            print(f"Ошибка при получении пользователя: {error}")
        except Exception as error:
            print(f"Ошибка при получении пользователя: {error}")

    async def update(self, id: UUID, **kwargs) -> Union[UUID, None, Exception]:
        try:
            query = update(User).where(User.id == id).values(
                kwargs).returning(User.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            user_id_row = res.fetchone()
            if user_id_row is not None:
                return user_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при обновлении пользователя")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка при обновлении пользователя")

    async def get_by_email(self, email: str) -> Union[User, None, Exception]:
        try:
            query = select(User).where(
                User.email == email, User.is_active == True)
            res = await self.db_session.execute(query)
            user_row = res.fetchone()
            if user_row is not None:
                return user_row[0]
        except exc.SQLAlchemyError as error:
            print(
                f"Ошибка SQLAlchemyError при получении пользователя по email {error}")
        except Exception as error:
            print(f"Неизвестная ошибка при получении пользователя по email")
