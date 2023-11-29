from abc import ABC, abstractclassmethod
from typing import Any
from uuid import UUID


class CrudBase(ABC):

    @abstractclassmethod
    async def create(self, name: str) -> Any:
        """Создание записи в таблице"""

    @abstractclassmethod
    async def delete(self, id: UUID | str) -> Any:
        """Удалеие записи в таблице"""

    @abstractclassmethod
    async def get(self, id: UUID) -> Any:
        """Получение записи из таблицы"""

    @abstractclassmethod
    async def update(self, id: UUID, **kwargs) -> Any:
        """Редактирование записи в таблице"""
