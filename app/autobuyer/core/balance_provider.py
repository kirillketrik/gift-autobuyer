from abc import ABC, abstractmethod


class BalanceProvider(ABC):
    """
    Интерфейс провайдера баланса Telegram-звёзд.

    Предоставляет метод для получения текущего баланса авторизованного пользователя (userbot).
    """

    @abstractmethod
    async def get_balance(self) -> int:
        """
        Получить текущий баланс пользователя в звёздах (Telegram stars).

        :return: Целое число — количество звёзд на счету пользователя.
        :raises NotAuthorizedError: Если клиент не авторизован в Telegram API.
        :raises FloodError: При слишком частых запросах.
        """
