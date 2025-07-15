from abc import ABC, abstractmethod

from app.core.interfaces.repository import GiftFilterReader, ReceiverReader
from .balance_provider import BalanceProvider
from .gift_allocator import GiftAllocator
from .gift_provider import GiftProvider
from .notifier import Notifier


class Autobuyer(ABC):
    @abstractmethod
    async def autobuy(
            self,
            gift_filter_reader: GiftFilterReader,
            receiver_reader: ReceiverReader,
            balance_provider: BalanceProvider,
            gift_provider: GiftProvider,
            gift_allocator: GiftAllocator,
            notifier: Notifier
    ) -> None:
        """
        Запускает процесс автоматической покупки подарков на основе заданных фильтров и текущего баланса.

        Последовательность операций:
          1. Чтение фильтров: Получает список активных фильтров, определяющих ограничения и предпочтения
             (цена, количество, supply, приоритет и др.).
          2. Чтение получателей: Получает список Telegram-пользователей, которым нужно отправить подарки.
          3. Получение баланса: Получает текущее количество звёзд, доступных на аккаунте.
          4. Получение подарков: Загружает список доступных для покупки подарков с маркетплейса.
          5. Распределение бюджета: Использует `GiftAllocator` для распределения баланса по фильтрам и
             подбору оптимального набора подарков для покупки.
          6. Покупка подарков: Выполняет транзакции покупки и отправки подарков получателям.
          7. Уведомление: Информирует об успехе, ошибках или отклонениях через `Notifier`.

        :param gift_filter_reader: Компонент, предоставляющий список фильтров подарков.
        :param receiver_reader: Компонент, предоставляющий список получателей.
        :param balance_provider: Компонент, возвращающий текущий баланс пользователя в звёздах.
        :param gift_provider: Компонент, отвечающий за получение списка подарков и выполнение покупки.
        :param gift_allocator: Компонент, распределяющий звёзды между подарками и фильтрами.
        :param notifier: Компонент, уведомляющий пользователя о результатах или ошибках.
        """
