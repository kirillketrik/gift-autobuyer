from abc import ABC, abstractmethod
from typing import List

from app.core.models.receiver import Receiver


class ReceiverReader(ABC):
    @abstractmethod
    async def get_all(self) -> List[Receiver]:
        """
        Возращает всех сохранённых получателей подарков
        :return: List[Receiver]
        """


class ReceiverWriter(ABC):
    @abstractmethod
    async def write_all(self, receivers: List[Receiver]) -> None:
        """
        Заменяет старых получаетелей на новых
        :param receivers: Список новых получателей
        """


class ReceiverRepository(ABC, ReceiverReader, ReceiverWriter):
    pass
