import logging
import logging.config

from fastapi import APIRouter, Depends, Header, Response, Cookie
from fastapi_pagination import LimitOffsetPage

from src.core.config import token_settings
from src.schemas.user import UserCreate, ChangeUserData, ChangeUserPassword, LoginRequest, UserResponse
from src.schemas.entry import EntryResponse
from src.utils.token_manager import verify_refresh_token, verify_access_token
from src.services.auth import AuthServiceBase, get_auth_service
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)

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
    log_msg = f'Login: {user}, {response=}, {auth_service}, {user_agent=}'
    log.debug(log_msg)
    access_token, refresh_token = await auth_service.login(user.email, user.password, user_agent)

    log_msg = f'{access_token=}, {refresh_token=}'
    log.debug(log_msg)
    log.info('Установить refresh token в cookie')
    response.set_cookie(
        key=token_settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=True,
        expires=token_settings.refresh_expire * 60  # sec
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
    log_msg = f'Refresh: {refresh_token}'
    log.debug(log_msg)
    new_access_token, new_refresh_token = await auth_service.refresh_tokens(refresh_token,
                                                                            user_agent)
    log.info('Установить refresh token в cookie')
    response.set_cookie(key=token_settings.refresh_token_cookie_name,
                        value=new_refresh_token,
                        httponly=True,
                        expires=token_settings.refresh_expire * 60)  # sec
    return new_access_token


@auth_router.get("/me",
                 response_model=UserResponse,
                 summary="Получить запрос на получение информации о пользователе",
                 description="Предоставляет информацию о пользователе с помощью токена доступа",
                 response_description="User data")
async def user_data(token: str = Depends(verify_access_token),
                    auth_service: AuthServiceBase = Depends(get_auth_service)) -> UserResponse:
    user_data = await auth_service.get_user_data(token)
    log_msg = f'{user_data=}, {token=}, {auth_service=}'
    log.debug(log_msg)
    return UserResponse.model_validate(user_data)


@auth_router.get("/entries",
                 response_model=LimitOffsetPage[EntryResponse],
                 summary="Получить запрос на историю записей пользователей",
                 description="Предоставляет пользователю доступ к записям с помощью токена доступа",
                 response_description="User entries")
async def user_entries(unique: bool = True,
                       token: str = Depends(verify_access_token),
                       auth_service: AuthServiceBase = Depends(
                           get_auth_service),
                       ) -> LimitOffsetPage[EntryResponse]:
    user_entries = await auth_service.entry_history(token, unique)
    return user_entries


@auth_router.get("/role",
                 response_model=list[str],
                 summary="Получить запрос на роли пользователей",
                 description="Предоставляет роли пользователям с помощью токена доступа",
                 response_description="User roles")
async def user_role(token: str = Depends(verify_access_token),
                    auth_service: AuthServiceBase = Depends(get_auth_service)) -> list[str]:
    roles = await auth_service.get_user_role(token)
    return roles


@auth_router.get("/logout",
                 summary="Получить запрос на выход из активного сеанса",
                 description="Закрывает сеанс пользователя и удаляет токены доступа и обновления",
                 response_description="None")
async def logout(response: Response,
                 access_token: str = Depends(verify_access_token),
                 refresh_token: str = Cookie(
                     include_in_schema=False, default=None),
                 user_agent: str = Header(include_in_schema=False),
                 auth_service: AuthServiceBase = Depends(get_auth_service)
                 ) -> None:
    await auth_service.logout(access_token, refresh_token, user_agent)
    log.debug('Удалить refresh token в cookie')
    response.delete_cookie(token_settings.refresh_token_cookie_name)


@auth_router.get("/logout_all",
                 summary="Получить запрос на выход из системы из всех активных сеансов",
                 description="Закрывает сеансы пользователя и удаляет токены доступа и обновления",
                 response_description="None")
async def logout_all(response: Response,
                     token: str = Depends(verify_access_token),
                     auth_service: AuthServiceBase = Depends(get_auth_service)) -> None:
    await auth_service.logout_all(token)
    log.debug('Удалить refresh token в cookie')
    response.delete_cookie(token_settings.refresh_token_cookie_name)


@auth_router.post("/change_pwd",
                  summary="Отправить запрос на изменение пароля пользователя",
                  description="Измените пароль пользователя и выйдите из системы",
                  response_description="None")
async def change_pwd(change_pwd_data: ChangeUserPassword,
                     response: Response,
                     access_token: str = Depends(verify_access_token),
                     refresh_token: str = Cookie(
                         include_in_schema=False, default=None),
                     auth_service: AuthServiceBase = Depends(get_auth_service)) -> None:
    log_msg = f'Изменить pwd: {change_pwd_data}'
    log.debug(log_msg)
    await auth_service.update_user_password(access_token,
                                            refresh_token,
                                            ChangeUserPassword(**change_pwd_data.model_dump(exclude_none=True)))
    log.debug('Удалить refresh token в cookie')
    response.delete_cookie(token_settings.refresh_token_cookie_name)


@auth_router.post("/change_user_data",
                  response_model=UserResponse,
                  summary="Опубликовать запрос на изменение информации о пользователе",
                  description="Изменить информацию о пользователе",
                  response_description="Информация о пользователе")
async def change_user_data(changed_user_data: ChangeUserData,
                           access_token: str = Depends(verify_access_token),
                           auth_service: AuthServiceBase = Depends(get_auth_service)) -> UserResponse:
    log_msg = f'Изменить данные пользователя: {changed_user_data}'
    log.debug(log_msg)
    updated_user = await auth_service.update_user_data(access_token, ChangeUserData(**changed_user_data.model_dump(exclude_none=True)))
    return UserResponse.model_validate(updated_user)


@auth_router.post("/deactivate_user",
                  summary="Отправить запрос на деактивацию пользователя",
                  description="Inactivate user's account",
                  response_description="None")
async def deactivфte_user(response: Response,
                          access_token: str = Depends(verify_access_token),
                          auth_service: AuthServiceBase = Depends(get_auth_service)):
    log_msg = f'Деактивация пользователя: {deactivфte_user}'
    log.debug(log_msg)
    await auth_service.deactivate_user(access_token)
    log.debug('Удалить refresh token в cookie')
    response.delete_cookie(token_settings.refresh_token_cookie_name)
