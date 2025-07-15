from abc import ABC, abstractmethod
from typing import List

from app.models import Gift, GiftAllocation, GiftFilter


class GiftAllocator(ABC):
    """
    Интерфейс для алгоритма распределения бюджета на покупку Telegram-подарков.

    Реализация должна принимать:
    - текущий баланс пользователя в звёздах;
    - список пользовательских фильтров (GiftFilter);
    - список доступных подарков (Gift).

    На выходе возвращается список GiftAllocation, описывающих, какие подарки и в каком количестве покупать.
    """

    @abstractmethod
    def get_allocations(self, balance: int, filters: List[GiftFilter], gifts: List[Gift]) -> List[GiftAllocation]:
        """
        Распределить бюджет и определить, какие подарки покупать на основе:
        - фильтров пользователя;
        - текущего баланса;
        - актуального списка подарков.

        Алгоритм должен учитывать параметры каждого фильтра:
        - включён ли фильтр (`enabled`);
        - диапазон цены (`min_price`, `max_price`);
        - диапазон саплая (`min_supply`, `max_supply`);
        - приоритет (`priority`);
        - лимит по количеству покупок (`max_buy_count`);
        - лимит по затратам (`max_spend_money`);
        - доля бюджета (`weight`).

        :param balance: Количество звёзд (stars) на балансе пользователя.
        :param filters: Список активных фильтров, по которым отбираются подарки.
        :param gifts: Список всех доступных подарков из Telegram.
        :return: Список аллокаций (GiftAllocation) — решений о покупке подарков.
        """
