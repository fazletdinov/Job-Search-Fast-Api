from typing import Annotated

from fastapi import Depends, Body, APIRouter, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_pagination import LimitOffsetPage
from fastapi_filter import FilterDepends

from .schema import ResumeCreate, ResumeRead, ResumeUpdate
from src.users.models import User
from src.users.router import users_roter
from src.auth.config import current_active_user
from database.session import get_async_session, engine
from .service import CrudResume
from .filter import ResumeFilter

resume_router = APIRouter()


@users_roter.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return user


@resume_router.post("/", response_model=ResumeRead)
async def add_resume(body: Annotated[ResumeCreate, Body()],
                     user: User = Depends(current_active_user)) -> ResumeRead:
    resume_dict: dict = body.model_dump(exclude_none=True)
    return await CrudResume._create_resume(resume_dict, user)


@resume_router.get("/{resume_id}", response_model=ResumeRead | None)
async def get_resume_by_id(resume_id: Annotated[int, Path(gt=0)],
                           db: Annotated[AsyncSession, Depends(get_async_session)]) -> ResumeRead | None:
    return await CrudResume._get_resume_by_id(resume_id, db)


@resume_router.get("/", response_model=LimitOffsetPage[ResumeRead])
async def get_list_resume(resume_filter: Annotated[ResumeFilter, FilterDepends(ResumeFilter)],
                          db: Annotated[AsyncSession, Depends(get_async_session)]) -> LimitOffsetPage[ResumeRead]:
    return await CrudResume._get_list_resume(resume_filter, db)


@resume_router.patch("/{resume_id}", response_model=ResumeRead)
async def update_resume(resume_id: Annotated[int, Path(gt=0)],
                        body: ResumeUpdate,
                        user: Annotated[User, Depends(current_active_user)]) -> ResumeRead:
    model_dump = body.model_dump(exclude_none=True)
    if model_dump is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Нужно заполнять хотбяы одно поля для обновления")
    return await CrudResume._update_resume(resume_id, user, model_dump)


@resume_router.delete("/{resume_id}")
async def delete_resume(resume_id: Annotated[int, Path(gt=0)],
                        user: Annotated[User, Depends(current_active_user)]) -> int:
    return await CrudResume._delete_resume(resume_id, user)
