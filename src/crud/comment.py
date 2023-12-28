from uuid import UUID
from typing import Union
import logging.config

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Comment
from src.crud.base_classes import CrudBase
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class CommentDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        log.debug("Инициализация CommentDAL")
        self.db_session = session

    async def create(self, vacansy_id: UUID, comment: dict, user_id: UUID) -> Union[Comment, None, Exception]:
        log_message = f'CRUD Создание Comment: vacansy_id={vacansy_id}, comment={comment}, user_id={user_id}'
        log.debug(log_message)
        try:
            comm: Comment = Comment(
                vacansy_id=vacansy_id, user_id=user_id, **comment)
            self.db_session.add(comm)
            await self.db_session.commit()
            return comm
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при создании Comment: vacansy_id={vacansy_id}, comment={comment}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создании Comment")
        except Exception as error:
            log_message = f"неизвестная ошибка при создании Comment: vacansy_id={vacansy_id}, comment={comment}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке создать Comment")

    async def get(self, vacansy_id: UUID) -> Union[list[Comment], None, Exception]:
        log_message = f'CRUD Получение Comment: vacansy_id={vacansy_id}'
        log.debug(log_message)
        try:
            query = select(Comment.id, Comment.text, Comment.created_at).where(
                Comment.vacansy_id == vacansy_id)
            res = await self.db_session.execute(query)
            comment_rows = res.fetchall()
            return comment_rows
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при получении Comment: vacansy_id={vacansy_id} {error}"
            log.exception(log_message)
        except Exception as error:
            log_message = f"неизвестная ошибка при получении Comment: vacansy_id={vacansy_id} {error}"

    async def delete(self, vacansy_id: UUID, comment_id: UUID, user_id: UUID) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление Comment: vacansy_id={vacansy_id}, comment_id={comment_id}, user_id={user_id}'
        log.debug(log_message)
        try:
            query = delete(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id ==
                                          comment_id, Comment.user_id == user_id).returning(Comment.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            comment_id_row = res.fetchone()
            if comment_id_row is not None:
                return comment_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении Comment: vacansy_id={vacansy_id}, comment_id={comment_id}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении Comment")
        except Exception as error:
            log_message = f"Неизвестная ошибка при удалении Comment: vacansy_id={vacansy_id}, comment_id={comment_id}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении Comment")

    async def admin_delete_comment_dal(self, vacansy_id: UUID, comment_id: UUID) -> Union[UUID, None, Exception]:
        log_message = f'CRUD Удаление админом Comment: vacansy_id={vacansy_id}, comment_id={comment_id}'
        log.debug(log_message)
        try:
            query = delete(Comment).where(
                Comment.vacansy_id == vacansy_id, Comment.id == comment_id).returning(Comment.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            comment_id_row = res.fetchone()
            if comment_id_row is not None:
                return comment_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при удалении админом Comment: vacansy_id={vacansy_id}, comment_id={comment_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении админом Comment")
        except Exception:
            log_message = f"Неизвестная ошибка при удалении админом Comment: vacansy_id={vacansy_id}, comment_id={comment_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении админом Comment")

    async def update(self, vacansy_id: UUID, comment_id: UUID, comment: dict, user_id: UUID) -> Union[
        UUID, None, Exception]:
        log_message = f'CRUD Обновление Comment: vacansy_id={vacansy_id}, comment_id={comment_id}, comment={comment}, user_id={user_id}'
        log.debug(log_message)
        try:
            query = update(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id == comment_id,
                                          Comment.user_id == user_id).values(**comment).returning(Comment.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            comment_id_row = res.fetchone()
            if comment_id_row is not None:
                return comment_id_row[0]
        except exc.SQLAlchemyError as error:
            log_message = f"Ошибка SQLAlchemyError при обновлении Comment: vacansy_id={vacansy_id}, comment_id={comment_id}, comment={comment}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Comment")
        except Exception:
            log_message = f"Неизвестная ошибка при обновлении Comment:  vacansy_id={vacansy_id}, comment_id={comment_id}, comment={comment}, user_id={user_id} {error}"
            log.exception(log_message)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при обновлении Comment")
