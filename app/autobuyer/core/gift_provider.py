from abc import ABC, abstractmethod
from typing import List

from app.models import Gift


class GiftProvider(ABC):
    """
    Интерфейс провайдера Telegram-подарков.

    Реализации этого интерфейса позволяют получать список доступных подарков
    и выполнять их покупку определённым пользователям.
    """

    @abstractmethod
    async def get_gifts(self) -> List[Gift]:
        """
        Получить список доступных подарков в Telegram.

        Метод возвращает только лимитированные подарки, доступные для покупки.
        Может использовать кеширование, если применимо.

        :return: Список объектов Gift, описывающих подарки.
        :raises NotAuthorizedError: Если клиент не авторизован.
        :raises FloodError: При слишком частых запросах.
        """

    @abstractmethod
    async def purchase(self, username: str, gift: Gift, hide_name: bool = True) -> None:
        """
        Купить подарок и отправить его пользователю.

        :param username: Username получателя подарка (без @).
        :param gift: Объект Gift, содержащий ID, цену и лимиты.
        :param hide_name: Если True, имя отправителя будет скрыто (анонимная отправка).
        :raises InsufficientBalanceError: Недостаточно средств на аккаунте.
        :raises NotAuthorizedError: Если клиент не авторизован.
        :raises GiftSoldOutError: Если подарок распродан.
        :raises FloodError: При слишком частых запросах.
        """
