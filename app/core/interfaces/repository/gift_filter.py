from abc import ABC, abstractmethod
from typing import List

from app.core.models import GiftFilter


class GiftFilterReader(ABC):
    @abstractmethod
    async def get_all(self) -> List[GiftFilter]:
        """
        Возвращает список всех добавленных фильтров для подарков
        :return: Список фильтров для подарков
        """


class GiftFilterWriter(ABC):
    @abstractmethod
    async def save(self, gift_filter: GiftFilter) -> GiftFilter:
        """
        Сохраняет фильтр
        :param gift_filter: Фильтр который нужно сохранить
        :return: Сохранённый фильтр
        """

    @abstractmethod
    async def delete(self, filter_ids: List[int]) -> None:
        """
        Удаляет фильтр по заданным id
        :param filter_ids: Список id фильтров, которые нужно удалить
        """


class GiftFilterRepository(GiftFilterReader, GiftFilterWriter, ABC):
    pass
