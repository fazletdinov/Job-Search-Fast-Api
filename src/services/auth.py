from abc import ABCMeta, abstractmethod
import logging.config
import bcrypt
from functools import lru_cache

from fastapi import status, HTTPException, Depends
from pydantic import SecretStr, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.token import TokenDBBase, get_token_db
from src.database.models import User as DBUser, Entry as DBEntry
from src.schemas import user as user_schema
from src.crud import user as user_dal, role as role_dal, entry as entry_dal
from src.utils.token_manager import TokenManagerBase, get_token_manager
from src.database.session import db_helper
from src.core.log_config import LOGGING

logging.config.dictConfig(LOGGING)
log = logging.getLogger(__name__)


class HashManagerBase(metaclass=ABCMeta):
    """Хэширование и проверка пароля"""

    @abstractmethod
    def hash_pwd(self, pwd: str) -> str:
        """Для получения hash пароля"""

    @abstractmethod
    def verify_pwd(self, pwd_in: str, pwd_hash: str) -> bool:
        """Проверка соответствия пароля"""


class AuthServiceBase(metaclass=ABCMeta):
    """Service для авторизации пользователя"""

    @abstractmethod
    async def register(self, user: user_schema.UserCreate) -> DBUser:
        """Регистрация нового пользовател"""

    @abstractmethod
    async def login(self, email: EmailStr, pwd: SecretStr, user_agent: str) -> tuple[str, str]:
        """Получение токенов доступа и обновления. Открытие новой сессии"""

    @abstractmethod
    async def logout(self, access_token: str, refresh_token: str, user_agent: str = None) -> None:
        """Сбросьте токены доступа и обновите. Закрытие сессии"""

    @abstractmethod
    async def logout_all(self, access_token: str) -> None:
        """Закрытие сесси всех активных пользователей"""

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str, user_agent: str) -> tuple[str, str]:
        """Обновить refresh token и access"""

    @abstractmethod
    async def get_user_data(self, access_token: str) -> DBEntry:
        """Получение пользователя"""

    @abstractmethod
    async def get_user_role(self, access_token: str) -> str:
        """Получение role пользователя"""

    @abstractmethod
    async def update_user_data(self, access_token: str, changed_data: user_schema.ChangeUserData) -> DBUser:
        """Изменение пользовательсктх данных"""

    @abstractmethod
    async def update_user_password(self, access_token: str, refresh_token: str,
                                   changed_data: user_schema.ChangeUserPassword) -> None:
        """Изменение пароля пользователя"""

    @abstractmethod
    async def entry_history(self, access_token: str, unique: bool) -> list[DBEntry]:
        """Получить историю входа пользователя в систему"""

    @abstractmethod
    async def deactivate_user(self, acces_token: str) -> None:
        """Деактивация пользователя"""


class AuthService(AuthServiceBase, HashManagerBase):

    def __init__(self,
                 token_db: TokenDBBase,
                 token_manager: TokenManagerBase,
                 user_db_session: AsyncSession) -> None:
        log.info("Инициализация authservice")
        self.token_db = token_db
        self.token_manager = token_manager
        self.user_db_session = user_db_session

    def hash_pwd(self, pwd: str) -> str:
        salt = bcrypt.gensalt()
        pwd_hash = bcrypt.hashpw(pwd.encode("utf-8"), salt)
        return pwd_hash.decode("utf-8")

    def verify_pwd(self, pwd_in: str, pwd_hash: str) -> bool:
        return bcrypt.checkpw(pwd_in.encode("utf-8"), pwd_hash.encode("utf-8"))

    async def register(self, user: user_schema.UserCreate) -> DBUser:
        async with self.user_db_session as session:
            async with session.begin():
                user_crud = user_dal.UserDAL(session)
                email_is_exist = await user_crud.get_by_email(user.email)
                log.debug(
                    f"email = {user.email}, email_is_exist = {email_is_exist}")
                if email_is_exist:
                    log.error(
                        f"Status code - {status.HTTP_400_BAD_REQUEST}: Пользователь уже существует")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Пользователь уже существует"
                    )
                log.debug(f"Создание нового пользователя: {user.email}")
                new_user = await user_crud.create(**user.model_dump(exclude={"password"}),
                                                  password=self.hash_pwd(user.password.get_secret_value()))
                return new_user

    async def _generate_tokens(self,
                               user: DBUser,
                               entry: DBEntry,
                               db_session: AsyncSession) -> tuple[str, str]:
        role_crud = role_dal.RoleDAL(db_session)
        roles = await role_crud.get_by_user_id(user.id)
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": [str(role.id) for role in roles] if roles else ["пользователь"]
        }
        access_token = await self.token_manager.generate_access_token(token_payload)
        token_payload.update({"session_id": str(entry.id)})
        refresh_token = await self.token_manager.generate_refresh_token(token_payload)
        return access_token, refresh_token

    async def login(self, email: EmailStr, pwd: SecretStr, user_agent: str) -> tuple[str, str]:
        async with self.user_db_session as session:
            async with session.begin():
                log_message = f'Login: {email}, pwd:{pwd}, user_agent:{user_agent}'
                log.debug(log_message)
                user_crud = user_dal.UserDAL(session)
                entry_crud = entry_dal.EntryDAL(session)
                user = await user_crud.get_by_email(email=email)
                log_message = f'Login: {email}, pwd:{pwd}, user_agent:{user_agent}'
                log.debug(log_message)
                if not user or not self.verify_pwd(pwd_in=pwd.get_secret_value(), pwd_hash=user.password):
                    log_message = (f"Login: {email}: "
                                   f"user is exist = {bool(user)}, "
                                   f"{self.verify_pwd(pwd.get_secret_value(), user.password)=}")
                    log.error(log_message)
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Некорректный пароль или email"
                    )
                if not user.is_active:
                    log.error(
                        f"{status.HTTP_400_BAD_REQUEST}: Ваш аккаунт не активен")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Ваш аккаунт не активен"
                    )
                exist_session = await entry_crud.get_by_user_agent(
                    user_agent, only_active=True)
                if exist_session:
                    log_msg = f'Login {user.email}: закрытие сессии (refresh = {exist_session.refresh_token})'
                    log.debug(log_msg)
                    await self._close_session(exist_session.refresh_token)

                access_token, refresh_token = await self._open_session(user, user_agent, session)
                log_msg = f'{access_token=}, {refresh_token=}'
                log.debug(log_msg)
                return access_token, refresh_token

    async def _open_session(self, user: DBUser, user_agent: str, db_session: AsyncSession) -> tuple[str, str]:
        log_msg = f'Open session (user = {user})'
        log.debug(log_msg)
        entry_crud = entry_dal.EntryDAL(db_session)
        # записать сессию в БД
        session = await entry_crud.create(user.id, user_agent, None)
        log.info('Generate new tokens')
        access_token, refresh_token = await self._generate_tokens(user, session, db_session)
        # записать токен в БД
        await entry_crud.update(session.id, refresh_token=refresh_token)
        return access_token, refresh_token

    async def _close_session(self, refresh_token: str) -> None:
        if refresh_token is None:
            return None
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        refresh_token_data = await self.token_manager.get_data_from_refresh_token(refresh_token)
        await entry_crud.delete(refresh_token_data.session_id)
        await self.token_db.put(refresh_token,
                                refresh_token_data.id,
                                refresh_token_data.left_time)

    async def logout(self, access_token: str, refresh_token: str, user_agent: str = None) -> None:
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        access_token_data = self.token_manager.get_data_from_access_token(
            access_token)
        user_id = access_token_data.sub
        # Добавить в redis истекшие токены
        await self.token_db.put(access_token, user_id, access_token_data.left_time)

        if refresh_token is None:
            session = await entry_crud.get_by_user_agent(user_agent, only_active=True)
            await self._close_session(session.refresh_token)
        else:
            await self._close_session(refresh_token)

    async def logout_all(self, access_token: str) -> None:
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        access_token_data = self.token_manager.get_data_from_access_token(
            access_token)
        user_id = access_token_data.sub
        await self.token_db.put(access_token, user_id, access_token_data.left_time)
        active_sessions = await entry_crud.get_by_user_id_list(user_id, only_active=True)
        for session in active_sessions:
            if session.refresh_token:
                await self._close_session(session.refresh_token)

    async def get_user_role(self, access_token: str) -> list[str] | str:
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        return token_data.role

    async def entry_history(self,
                            access_token: str,
                            unique: bool,
                            page_size: int,
                            page_number: int) -> list[DBEntry]:
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        entry_history = await entry_crud.get_by_user_id_list(token_data.sub, unique)
        return entry_history

    async def get_user_data(self, access_token: str) -> DBUser:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        user = await user_crud.get(token_data.sub)
        return user

    async def update_user_data(self, access_token: str, changed_data: user_schema.ChangeUserData) -> DBUser:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        update_user_id = await user_crud.update(token_data.sub, changed_data.model_dump(exclude_none=True))
        update_user = await user_crud.get(update_user_id)
        return update_user

    async def update_user_password(self, access_token: str, refresh_token: str,
                                   changed_data: user_schema.ChangeUserPassword) -> None:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(access_token)
        # проверка старого пороля
        user = await user_crud.get(token_data.sub)
        if not self.verify_pwd(changed_data.old_password.get_secret_value(), user.password):
            log.error(
                f"{status.HTTP_403_FORBIDDEN}: Неккоректный старый пароль")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Неккоректный старый пароль")
        # добавление нового пароля
        await user_crud.update(token_data.sub, password=self.hash_pwd(changed_data.new_password.get_secret_value()))
        log.info('Выход из системы после смены пароля')
        await self.logout(access_token, refresh_token)

    async def refresh_tokens(self, refresh_token: str, user_agent: str) -> tuple[str, str]:
        user_crud = user_dal.UserDAL(self.user_db_session)
        entry_crud = entry_dal.EntryDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_refresh_token(refresh_token)
        log.info('Закроет старую сессию после обновления токенов')
        await self._close_session(refresh_token)
        # получить пользователя по id
        user = await user_crud.get(token_data.sub)
        # записать сессию в БД
        session = await entry_crud.create(user.id, user_agent, None)
        log.info('Генерация нового токена')
        access_token, refresh_token = await self._generate_tokens(user, session)
        # записать токен в БД
        await entry_crud.update(session.id, refresh_token=refresh_token)
        return access_token, refresh_token

    async def deactivate_user(self, acces_token: str) -> None:
        user_crud = user_dal.UserDAL(self.user_db_session)
        token_data = await self.token_manager.get_data_from_access_token(acces_token)
        await self.logout_all(acces_token)
        await user_crud.delete(token_data.sub)


@lru_cache
def get_auth_service(token_db: TokenDBBase = Depends(get_token_db),
                     token_manager: TokenManagerBase = Depends(
                         get_token_manager),
                     user_db_session: AsyncSession = Depends(db_helper.get_async_session)):
    log_msg = f'{token_db=}, {token_manager=}, {user_db_session=}'
    log.debug(log_msg)
    return AuthService(token_db, token_manager, user_db_session)
