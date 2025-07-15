from abc import ABC, abstractmethod

from app.autobuyer.balance_provider import BalanceProvider
from app.autobuyer.notifier import Notifier
from app.core.interfaces.repository import GiftFilterReader, ReceiverReader
from .gift_provider import GiftProvider


class Autobuyer(ABC):
    @abstractmethod
    async def autobuy(
            self,
            gift_filter_reader: GiftFilterReader,
            receiver_reader: ReceiverReader,
            balance_provider: BalanceProvider,
            gift_provider: GiftProvider,
            notifier: Notifier
    ) -> None:
        """
        Основной интерфейс для реализации автоматической покупки подарков.

        Выполняет следующие действия:
          1. Получает фильтры подарков от пользователя.
          2. Получает текущий баланс аккаунта.
          3. Получает список доступных подарков.
          4. Сопоставляет подарки с фильтрами, распределяет бюджет.
          5. Покупает подходящие подарки для получателей.
          6. Отправляет уведомления о результатах.

        :param gift_filter_reader: Источник фильтров, определяющих какие подарки покупать.
        :param receiver_reader: Источник списка получателей подарков.
        :param balance_provider: Поставщик информации о текущем балансе пользователя (в звёздах).
        :param gift_provider: Провайдер подарков — получает список доступных и выполняет покупку.
        :param notifier: Система уведомлений — для информирования о событиях и ошибках.
        """
