from typing import Annotated

from fastapi import Depends, Body, APIRouter, Path, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from .schemas import ResumeCreate, ResumeRead, ResumeUpdate, VacansyCreate, VacansyRead, VacansyUpdate
from .models import User
from .router import users_roter
from .config import current_active_user
from .dals import ResumeDal, VacansyDal
from database.session import get_async_session, engine

resume_router = APIRouter()
vacansy_router = APIRouter()


@users_roter.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return user


async def _create_resume(body: ResumeCreate, user: User) -> ResumeRead:
    async with engine.begin() as conn:
        resumedal = ResumeDal(conn)
        resume = await resumedal.create_resume_dal(first_name=body.first_name, last_name=body.last_name,
                                               middle_name=body.middle_name, age=body.age, experience=body.experience,
                                               education=body.education, about=body.about, user=user)
        return ResumeRead(id=resume.id, first_name=resume.first_name, last_name=resume.last_name,
                          middle_name=resume.middle_name, age=resume.age, experience=resume.experience,
                          education=resume.education, about=resume.about, user_id=resume.user_id)


async def _get_resume_by_id(resume_id: int, db: AsyncSession) -> ResumeRead:
    async with db as session:
        async with session.begin():
            resumedal = ResumeDal(session)
            resume = await resumedal.get_resume_by_id_dal(resume_id)
            return resume[0]


async def _update_resume(resume_id: int, user: User, kwargs) -> ResumeRead:
    async with engine.begin() as conn:
        resumedal = ResumeDal(conn)
        resume = await resumedal.update_resume_dal(resume_id, user, kwargs)
        return resume


async def _delete_resume(resume_id: int, user: User) -> int:
    async with engine.begin() as conn:
        resumedal = ResumeDal(conn)
        resume = await resumedal.delete_resume_dal(resume_id, user)
        return resume
    
async def _create_vacansy(vacansy: dict, user: User) -> VacansyRead:
    async with engine.begin() as conn:
        vacansydal = VacansyDal(conn)
        vacansy = await vacansydal.create_vacansy_dal(vacansy, user)
        return vacansy
    
async def _get_vacansy_by_id(vacansy_id: int, db: AsyncSession) -> VacansyRead:
    async with db as session:
        async with session.begin():
            vacansydal = VacansyDal(session)
            vacansy = await vacansydal.get_vacansy_by_id_dal(vacansy_id)
            return vacansy[0]

async def _update_vacansy(vacansy_id: int, body: dict, user: User) -> int:
    async with engine.begin() as conn:
        vacansydal = VacansyDal(conn)
        vacansy = await vacansydal.update_vacansy_dal(vacansy_id, body, user)
        return vacansy

async def _delete_vacansy(vacansy_id: int, user: User):
    async with engine.begin() as conn:
        vacansydal = VacansyDal(conn)
        return await vacansydal.delete_vacansy_dal(vacansy_id, user)

@resume_router.post("/", response_model=ResumeRead)
async def add_resume(body: Annotated[ResumeCreate, Body()],
                     user: User = Depends(current_active_user)) -> ResumeRead:

    return await _create_resume(body, user)


@resume_router.get("/{resume_id}", response_model=ResumeRead | None)
async def get_resume_by_id(resume_id: Annotated[int, Path(gt=0)],
                           db: Annotated[AsyncSession, Depends(get_async_session)]) -> ResumeRead | None:
    return await _get_resume_by_id(resume_id, db)


@resume_router.patch("/{resume_id}", response_model=ResumeRead)
async def update_resume(resume_id: Annotated[int, Path(gt=0)],
                        body: ResumeUpdate,
                        user: Annotated[User, Depends(current_active_user)]) -> ResumeRead:
    model_dump = body.model_dump(exclude_none=True)
    if model_dump is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Нужно заполнять хотбяы одно поля для обновления")
    return await _update_resume(resume_id, user, model_dump)


@resume_router.delete("/{resume_id}")
async def delete_resume(resume_id: Annotated[int, Path(gt=0)],
                        user: Annotated[User, Depends(current_active_user)]) -> int:
    return await _delete_resume(resume_id, user)


@vacansy_router.post("/", response_model=VacansyRead)
async def add_vacansy(vacansy: VacansyCreate, user: Annotated[User, Depends(current_active_user)]) -> VacansyRead:
    vacansy_dict: dict = vacansy.model_dump(exclude_none=True)
    return await _create_vacansy(vacansy_dict, user)

@vacansy_router.get("/{vacansy_id}", response_model=VacansyRead)
async def get_vacansy_by_id(vacansy_id: Annotated[int, Path(gt=0)],
                            db: Annotated[AsyncSession, Depends(get_async_session)]):
    return await _get_vacansy_by_id(vacansy_id, db)

@vacansy_router.patch("/{vacansy_id}")
async def update_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         body: VacansyUpdate,
                         user: Annotated[User, Depends(current_active_user)]) -> int:
    vacansy_dict: dict = body.model_dump(exclude_none=True)
    if vacansy_dict is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail="Необходимо заполнить хотябы одно поле")
    return await _update_vacansy(vacansy_id, vacansy_dict, user)

@vacansy_router.delete("/{vacansy_id}")
async def delete_vacansy(vacansy_id: Annotated[int, Path(gt=0)],
                         user: Annotated[User, Depends(current_active_user)]):
    return await _delete_vacansy(vacansy_id, user)