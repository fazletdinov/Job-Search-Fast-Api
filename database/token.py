from abc import ABC, abstractclassmethod

import backoff
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from src.core.config import redis_settings

class TokenDBBase(ABC):

    @abstractclassmethod
    async def put(self, token: str, user_id: str, expire_in_sec: int) -> None:
        """Добавить токен в базу данных токенов

        Args:
            token (str): 
            user_id (str): 
            expire_in_sec (int):
        """
        pass

    @abstractclassmethod
    async def is_exists(self, token: str) -> bool:
        """Проверьте, существует ли токен

        Args:
            token (str):

        Returns:
            bool:
        """
        pass


class TokenDB(TokenDBBase):
    def __init__(self, host: str, port: int, password: str) -> None:
        self.redis = Redis(host=host, port=port, password=password)

    @backoff.on_exception(backoff.expo, (RedisConnectionError), max_tries=5, raise_on_giveup=True)
    async def put(self, token: str, user_id: str, expire_in_sec: int) -> None:
        await self.redis.set(token, user_id, expire_in_sec)

    @backoff.on_exception(backoff.expo, (RedisConnectionError), max_tries=5, raise_on_giveup=True)
    async def is_exists(self, token: str) -> bool:
        is_exists = await self.redis.exists(token)
        return is_exists

@backoff.on_exception(backoff.expo, (RedisConnectionError), max_tries=5, raise_on_giveup=True)
async def get_token_db() -> TokenDBBase:
    return TokenDB(redis_settings.host, redis_settings.port, redis_settings.password.get_secret_value())
