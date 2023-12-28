from abc import ABCMeta, abstractmethod
from typing import Any


class CrudBase(metaclass=ABCMeta):

    @abstractmethod
    async def create(self) -> Any:
        """Создание записи в таблице"""

    @abstractmethod
    async def delete(self) -> Any:
        """Удалеие записи в таблице"""

    @abstractmethod
    async def get(self) -> Any:
        """Получение записи из таблицы"""

    @abstractmethod
    async def update(self) -> Any:
        """Редактирование записи в таблице"""
