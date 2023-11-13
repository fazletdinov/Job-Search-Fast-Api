from typing import Annotated
import logging

from fastapi import APIRouter, Depends, Header, Response, Cookie, Query
from fastapi_pagination import LimitOffsetPage

from core.config import token_settings
from src.schemas.user import UserCreate, ChangeUserData, ChangeUserPassword, LoginRequest, UserResponse
from src.schemas.entry import EntryResponse
from utils.token_manager import get_token_manager, verify_refresh_token, verify_access_token
from src.services.auth import AuthServiceBase, get_auth_service


auth_router = APIRouter(prefix="/auth")

@auth_router.post("/register",
                  response_model=UserResponse,
                  summary="Отправить запрос на регистрацию нового пользователя",
                  description="Создает нового пользователя и возвращает новый пользовательский объект",
                  response_description="Новые данные для авторизации пользователя")

async def register(user: UserCreate,
                   auth_service: AuthServiceBase = Depends(get_auth_service)):
    register_user = await auth_service.register(UserCreate(**user.model_dump(exclude_none=True)))
    return UserResponse.model_validate(register_user)


@auth_router.post("/login",
                  response_model=str,
                  summary="Отправить запрос на вход существующего пользователя",
                  description="Создает токены доступа и обновления",
                  response_description="Access token")
async def login(user: LoginRequest,
                response: Response,
                auth_service: AuthServiceBase = Depends(get_auth_service),
                user_agent: str = Header(include_in_schema=False)) -> str:
    access_token, refresh_token = await auth_service.login(user.email, user.password, user_agent)
    response.set_cookie(
        key=token_settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=True,
        expires=token_settings.refresh_expire * 60 # sec
    )
    return access_token

@auth_router.post("/refresh",
                  response_model=str,
                  summary="Отправить запрос на обновление токена доступа",
                  description="Создает новые токены доступа и обновления",
                  response_description="Новый access token")
async def refresh(response: Response,
                  auth_service: AuthServiceBase = Depends(get_auth_service),
                  refresh_token: str = Depends(verify_refresh_token),
                  user_agent: str = Header(include_in_schema=False), 
                  ) -> str:
    new_access_token, new_refresh_token = await auth_service.refresh_tokens(refresh_token,
                                                                            user_agent)
    response.set_cookie(key=token_settings.refresh_token_cookie_name,
                        value=new_refresh_token,
                        httponly=True,
                        expires=token_settings.refresh_expire * 60) # sec
    return new_access_token


@auth_router.get("/me",
                 response_model=UserResponse,
                 summary="Получить запрос на получение информации о пользователе",
                 description="Предоставляет информацию о пользователе с помощью токена доступа",
                 response_description="User data")
async def user_data(token: str = Depends(verify_access_token),
                    auth_service: AuthServiceBase = Depends(get_auth_service)) -> UserResponse:
    user_data = await auth_service.get_user_data(token)
    return UserResponse.model_validate(user_data)

@auth_router.get("/entries",
                 response_model=LimitOffsetPage[EntryResponse],
                 summary="Получить запрос на историю записей пользователей",
                 description="Предоставляет пользователю доступ к записям с помощью токена доступа",
                 response_description="User entries")
async def user_entries(unique: bool = True,
                       token: str = Depends(verify_access_token),
                       auth_service: AuthServiceBase = Depends(get_auth_service),
                       ) -> LimitOffsetPage[EntryResponse]:
    user_entries = await auth_service.entry_history(token, unique)
    return user_entries
