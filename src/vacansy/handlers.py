from typing import Annotated

from fastapi import Depends, APIRouter, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import LimitOffsetPage
from fastapi_filter import FilterDepends

from .schema import (VacansyCreate, VacansyRead, VacansyUpdate, VacansyReadList,
                     CommentCreate, CommentRead, CommentUpdate, VacansyReadAfterPost)
from database.models import User
from src.auth.config import current_active_user, current_active_superuser
from database.session import get_async_session
from .service import CrudVacansy, CrudComment
from .filter import VacansyFilter
from src.users.permissions import Permission

vacansy_router = APIRouter()


@vacansy_router.post("/", response_model=VacansyReadAfterPost)
async def add_vacansy(vacansy: VacansyCreate,
                      user: Annotated[User, Depends(current_active_user)],
                      db: Annotated[AsyncSession, Depends(get_async_session)]) -> VacansyReadAfterPost:
    vacansy_dict: dict = vacansy.model_dump(exclude_none=True)
    return await CrudVacansy._create_vacansy(vacansy_dict, user, db)


@vacansy_router.get("/{vacansy_id}", response_model=VacansyRead)
async def get_vacansy_by_id(vacansy_id: Annotated[int, Path(gt=0)],
                            db: Annotated[AsyncSession, Depends(get_async_session)]):
    vacansy = await CrudVacansy._get_vacansy_by_id(vacansy_id, db)
    if vacansy is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Вакансии с id = {vacansy_id} не существует")
    return vacansy


@vacansy_router.get("/", response_model=LimitOffsetPage[VacansyReadList])
async def get_list_vacansy(vacansy_filter: Annotated[VacansyFilter, FilterDepends(VacansyFilter)],
                           db: Annotated[AsyncSession, Depends(get_async_session)]):
    return await CrudVacansy._get_list_vacansy(vacansy_filter, db)


@vacansy_router.patch("/{vacansy_id}", response_model=int)
async def update_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         body: VacansyUpdate,
                         user: Annotated[User, Depends(current_active_user)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]) -> int:
    vacansy_dict: dict = body.model_dump(exclude_none=True)
    if vacansy_dict is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Необходимо заполнить хотябы одно поле")
    return await CrudVacansy._update_vacansy(vacansy_id, vacansy_dict, user, db)


@vacansy_router.delete("/{vacansy_id}", response_model=int)
async def delete_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         user: Annotated[User, Depends(current_active_user)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]) -> int:
    if not Permission.check_user_permission(user):
        return await CrudVacansy._admin_delete_vacansy(vacansy_id, user, db)
    vacansy_id = await CrudVacansy._delete_vacansy(vacansy_id, user, db)
    if vacansy_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Вакансии с id = {vacansy_id} не существует")
    return vacansy_id

@vacansy_router.delete("/admin/{vacansy_id}", response_model=int)
async def admin_delete_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         user: Annotated[User, Depends(current_active_superuser)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]) -> int:
    
    vacansy_id = await CrudVacansy._admin_delete_vacansy(vacansy_id, user, db)
    if vacansy_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=f"Вакансии с id = {vacansy_id} не существует")
    return vacansy_id


@vacansy_router.post("/{vacansy_id}/comments", response_model=CommentRead)
async def create_comment(vacansy_id: Annotated[int, Path(gt=0)],
                         body: CommentCreate,
                         user: Annotated[User, Depends(current_active_user)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]):
    comment: dict = body.model_dump(exclude_none=True)
    return await CrudComment._create_comment(vacansy_id, comment, user, db)


@vacansy_router.get("/{vacansy_id}/comments", response_model=list[CommentRead] | None)
async def get_list_comments(vacansy_id: Annotated[int, Path(gt=0)],
                            db: Annotated[AsyncSession, Depends(get_async_session)]):
    return await CrudComment._get_list_comments(vacansy_id, db)


@vacansy_router.delete("/{vacansy_id}/{comment_id}")
async def delete_comment(vacansy_id: Annotated[int, Path(gt=0)],
                         comment_id: Annotated[int, Path(gt=0)],
                         user: Annotated[User, Depends(current_active_user)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]) -> int:
    if not Permission.check_user_permission(user):
        return await CrudComment._admin_delete_comment(vacansy_id, comment_id, user, db)
    res = await CrudComment._delete_comment(vacansy_id, comment_id, user, db)
    if res is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Комментарий или вакансия не существуют")

@vacansy_router.delete("/admin/{vacansy_id}/{comment_id}")
async def admin_delete_comment(vacansy_id: Annotated[int, Path(gt=0)],
                         comment_id: Annotated[int, Path(gt=0)],
                         user: Annotated[User, Depends(current_active_superuser)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]) -> int:
    res = await CrudComment._admin_delete_comment(vacansy_id, comment_id, user, db)
    if res is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Комментарий или вакансия не существуют")
    return res


@vacansy_router.patch("/{vacansy_id}/{comment_id}")
async def update_comment(vacansy_id: Annotated[int, Path(gt=0)],
                         comment_id: Annotated[int, Path(gt=0)],
                         body: CommentUpdate,
                         user: Annotated[User, Depends(current_active_user)],
                         db: Annotated[AsyncSession, Depends(get_async_session)]):
    comment = body.model_dump(exclude_none=True)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Необходимо заполнить хотябы одно поле")
    return await CrudComment._update_comment(vacansy_id, comment_id, comment, user, db)
