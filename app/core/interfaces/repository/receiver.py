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
    async def save(self, receiver: Receiver) -> None:
        """
        Сохраняет получателя подарков
        :param receiver: Получатель подарка
        """

    @abstractmethod
    async def delete(self, receiver_ids: List[int]) -> None:
        """
        Удаляет получателей с указанными id
        :param receiver_ids: ID получателей для удаления
        """


class ReceiverRepository(ABC, ReceiverReader, ReceiverWriter):
    pass
