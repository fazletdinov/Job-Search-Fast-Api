from typing import Annotated

from fastapi import Depends, APIRouter, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import LimitOffsetPage
from fastapi_filter import FilterDepends

from .schema import VacansyCreate, VacansyRead, VacansyUpdate
from src.users.models import User
from src.auth.config import current_active_user
from database.session import get_async_session, engine
from .service import CrudVacansy
from .filter import VacansyFilter

vacansy_router = APIRouter()

@vacansy_router.post("/", response_model=VacansyRead)
async def add_vacansy(vacansy: VacansyCreate, user: Annotated[User, Depends(current_active_user)]) -> VacansyRead:
    vacansy_dict: dict = vacansy.model_dump(exclude_none=True)
    return await CrudVacansy._create_vacansy(vacansy_dict, user)


@vacansy_router.get("/{vacansy_id}", response_model=VacansyRead)
async def get_vacansy_by_id(vacansy_id: Annotated[int, Path(gt=0)],
                            db: Annotated[AsyncSession, Depends(get_async_session)]):
    return await CrudVacansy._get_vacansy_by_id(vacansy_id, db)


@vacansy_router.get("/", response_model=LimitOffsetPage[VacansyRead])
async def get_list_vacansy(vacansy_filter: Annotated[VacansyFilter, FilterDepends(VacansyFilter)],
                           db: Annotated[AsyncSession, Depends(get_async_session)]):
    return await CrudVacansy._get_list_vacansy(vacansy_filter, db)


@vacansy_router.patch("/{vacansy_id}")
async def update_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         body: VacansyUpdate,
                         user: Annotated[User, Depends(current_active_user)]) -> int:
    vacansy_dict: dict = body.model_dump(exclude_none=True)
    if vacansy_dict is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Необходимо заполнить хотябы одно поле")
    return await CrudVacansy._update_vacansy(vacansy_id, vacansy_dict, user)


@vacansy_router.delete("/{vacansy_id}")
async def delete_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         user: Annotated[User, Depends(current_active_user)]):
    return await CrudVacansy._delete_vacansy(vacansy_id, user)