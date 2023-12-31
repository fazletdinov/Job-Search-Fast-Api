from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import status, HTTPException, Depends, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from pydantic import ValidationError

from src.core.config import settings
from src.schemas import token as token_schema
from src.database.token import TokenDBBase, get_token_db


async def _verify_token(token: str, token_db: TokenDBBase, type: token_schema.TokenType) -> str:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        if type == token_schema.TokenType.access.value:
            secret_key = settings.token.access_secret_key
            payload_model = token_schema.AccessTokenPayload
        else:
            secret_key = settings.token.refresh_secret_key
            payload_model = token_schema.AccessTokenPayload

        payload = jwt.decode(
            token,
            secret_key.get_secret_value(),
            algorithms=[settings.token.algorithm],
            options={"verify_exp": False, },
        )

        token_data = payload_model(**payload)

        expired = await token_db.is_exist(token)
        if token_data.exp < datetime.now(timezone.utc) or expired:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired',
                headers={'WWW-Authenticate': 'Bearer'},
            )

    except (Exception, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return token


async def verify_access_token(authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False)),
                              token_db: TokenDBBase = Depends(get_token_db),
                              ) -> str:
    token = authorization.credentials if authorization is not None else None
    token = await _verify_token(token, token_db, token_schema.TokenType.access.value)
    return token


async def verify_refresh_token(refresh_token: str = Cookie(None, include_in_schema=False),
                               token_db: TokenDBBase = Depends(get_token_db),
                               ) -> str:
    token = await _verify_token(refresh_token, token_db, token_schema.TokenType.refresh.value)
    return token


class TokenManagerBase(ABC):
    @abstractmethod
    async def generate_access_token(self) -> str:
        """Создать access token"""

    @abstractmethod
    async def generate_refresh_token(self) -> str:
        """Создать refresh token"""

    @abstractmethod
    async def get_data_from_access_token(self) -> token_schema.TokenPayloadsBase:
        """Получение данных из access token"""

    @abstractmethod
    async def get_data_from_refresh_token(self) -> token_schema.TokenPayloadsBase:
        """Получение данных из refresh token"""


class TokenManager(TokenManagerBase):

    def __init__(self, token_db: TokenDBBase) -> None:
        self.token_db = token_db

    async def _generate_token(self,
                              data: dict[str, Any],
                              expires_delta: int,
                              secret_key: str,
                              algorithm: str,
                              payload_model: token_schema.TokenPayloadsBase,
                              ) -> str:
        expires_delta = datetime.utcnow() + timedelta(minutes=expires_delta)
        token_payload = payload_model(**data, exp=expires_delta)
        encode_jwt = jwt.encode(token_payload.dict(), secret_key, algorithm)
        return encode_jwt

    async def generate_access_token(self, data: dict[str, Any]) -> str:
        access_token = await self._generate_token(data=data,
                                                  expires_delta=token_settings.access_expire,
                                                  secret_key=token_settings.access_secret_key.get_secret_value(),
                                                  algorithm=token_settings.algorithm,
                                                  payload_model=token_schema.AccessTokenPayload)
        return access_token

    async def generate_refresh_token(self, data: dict[str, Any]) -> str:
        refresh_token = await self._generate_token(data=data,
                                                   expires_delta=token_settings.refresh_expire,
                                                   secret_key=token_settings.refresh_secret_key.get_secret_value(),
                                                   algorithm=token_settings.algorithm,
                                                   payload_model=token_schema.RefreshTokenPayload)
        return refresh_token

    async def _get_data_from_token(self,
                                   token: str,
                                   secret_key: str,
                                   algorithm: str,
                                   payload_model: token_schema.TokenPayloadsBase) -> token_schema.TokenPayloadsBase:
        payload = jwt.decode(token=token,
                             key=secret_key,
                             algorithms=[algorithm],
                             options={"verify_exp": False})
        return payload_model(**payload)

    async def get_data_from_access_token(self, token: str) -> token_schema.AccessTokenPayload:
        token_data = await self._get_data_from_token(token=token,
                                                     secret_key=token_settings.access_secret_key.get_secret_value(),
                                                     algorithm=token_settings.algorithm,
                                                     payload_model=token_schema.AccessTokenPayload)
        return token_data

    async def get_data_from_refresh_token(self, token: str) -> token_schema.RefreshTokenPayload:
        token_data = await self._get_data_from_token(token=token,
                                                     secret_key=token_settings.refresh_secret_key.get_secret_value(),
                                                     algorithm=token_settings.algorithm,
                                                     payload_model=token_schema.RefreshTokenPayload)
        return token_data


async def get_token_manager(token_db: TokenDBBase = Depends(get_token_db)) -> TokenManagerBase:
    return TokenManager(token_db)
