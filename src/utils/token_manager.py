from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from fastapi import status, HTTPException, Depends, Cookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt, JWTError
from pydantic import ValidationError

from core.config import token_settings
from schemas import token as token_schema
from database.token import TokenDBBase, get_token_db


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
    async def get_data_refresh_token(self) -> token_schema.TokenPayloadsBase:
        """Получение данных из refresh token"""

    @abstractmethod
    async def verify_access_token(self) -> str:
        """Верификация access token"""

    @abstractmethod
    async def verify_refresh_token(self) -> str:
        """Верицикация refresh token""" 


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
    
    async def _verify_token(self, token: str, token_db: TokenDBBase, type: token_schema.TokenType) -> str:
        if token is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Не удалось подтвердить учетные данные"
                headers={"WWW-Authenticate": "Bearer"}
            )
        try:
            if type == token_schema.TokenType.access.value:
                secret_key = token_settings.access_secret_key
                payload_model = token_schema.AccessTokenPayload
            else:
                secret_key = token_settings.refresh_secret_key
                payload_model = token_schema.RefreshTokenPayload
            
            payload = jwt.decode(
                token=token,
                key=secret_key.get_secret_value(),
                algorithms=[token_settings.algorithm],
                options={"verify_exp": False}
            )
            token_data = payload_model(**payload)

            expired = await token_db.is_exists(token)
            if token_data.exp < datetime.now(timezone.utc) or expired:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Срок Токена истек",
                    headers={"WWW-Authenticate": "Bearer"}
                )
        except (JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Не удалось подтвердить учетные данные"
                headers={"WWW-Authenticate": "Bearer"}
            )
        return token

    async def verify_access_token(self, authorization: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=True)),
                                  ) -> str:
        
        token = authorization.credentials if authorization is not None else None
        token = await self._verify_token(token, self.token_db, token_schema.TokenType.access.value)
        return token

    async def verify_refresh_token(self, refresh_token: str = Cookie(None, include_in_schema=False),
                                   ) -> str:
        token = await self._verify_token(refresh_token, self.token_db, token_schema.TokenType.refresh.value)
        return token
    
async def get_token_manager(token_db: TokenDBBase = Depends(get_token_db)) -> TokenManagerBase:
    return TokenManager(token_db)

        


    