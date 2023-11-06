from uuid import UUID
from typing import Union

from fastapi import status, HTTPException
from sqlalchemy import select, update, exc, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Comment
from src.crud.base_classes import CrudBase


class CommentDAL(CrudBase):

    def __init__(self, session: AsyncSession) -> None:
        self.db_session = session

    async def create(self, vacansy_id: UUID, comment: dict, user_id: UUID) -> Union[Comment, None, Exception]:
        try:
            comm: Comment = Comment(vacansy_id=vacansy_id, user_id=user_id, **comment)
            self.db_session.add(comm)
            await self.db_session.commit()
            return comm
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при создании Comment")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при попытке создать Comment")
    
    async def get(self, vacansy_id: UUID) -> Union[list[Comment], None, Exception]:
        try:
            query = select(Comment.id, Comment.text, Comment.created).where(Comment.vacansy_id == vacansy_id)
            res = await self.db_session.execute(query)
            comment_rows = res.fetchall()
            return comment_rows
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAclhemyError при получении Comment")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при получении Comment")
    
    async def delete(self, vacansy_id: UUID, comment_id: UUID, user_id: UUID) -> Union[UUID, None, Exception]:
        try:
            query = delete(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id == comment_id, Comment.user_id == user_id).returning(Comment.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            comment_id_row = res.fetchone()
            if comment_id_row is not None:
                return comment_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении Comment")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении Comment") 
    
    async def admin_delete_comment_dal(self, vacansy_id: UUID, comment_id: UUID) -> Union[UUID, None, Exception]:
        try:
            query = delete(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id == comment_id).returning(Comment.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            comment_id_row = res.fetchone()
            if comment_id_row is not None:
                return comment_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при удалении админом Comment")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении админом Comment")
            
    async def update(self, vacansy_id: UUID, comment_id: UUID, comment: dict, user_id: UUID) -> Union[UUID, None, Exception]:
        try:
            query = update(Comment).where(Comment.vacansy_id == vacansy_id, Comment.id == comment_id,
                                          Comment.user_id == user_id).values(**comment).returning(Comment.id)
            res = await self.db_session.execute(query)
            await self.db_session.commit()
            comment_id_row = res.fetchone()
            if comment_id_row is not None:
                return comment_id_row[0]
        except exc.SQLAlchemyError:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Ошибка SQLAlchemyError при обновлении Comment")
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Неизвестная ошибка при удалении Comment")