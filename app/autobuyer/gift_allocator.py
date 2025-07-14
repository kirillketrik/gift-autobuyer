from abc import ABC, abstractmethod
from typing import List

from app.models import Gift, GiftAllocation
from app.models import GiftFilter


class GiftAllocator(ABC):
    @abstractmethod
    def get_allocations(self, balance: int, gifts: List[Gift]) -> List[GiftAllocation]:
        ...


class DefaultGiftAllocator(GiftAllocator):
    def __init__(self, gift_filters: List[GiftFilter]):
        self.gift_filters: List[GiftFilter] = [g for g in gift_filters if g.enabled]
        self.total_weight = sum(f.weight for f in self.gift_filters)

    def get_allocations(self, balance: int, gifts: List[Gift]) -> List[GiftAllocation]:
        allocations = []

        for gift_filter in self.gift_filters:
            order, field = gift_filter.ordering[0], gift_filter.ordering[1:]

            valid_gifts = sorted(
                [g for g in gifts if gift_filter.match(g)],
                key=lambda g: getattr(g, field, 0),
                reverse=order
            )

            if len(valid_gifts) == 0:
                continue

            if gift_filter.weight > 0:
                budget = balance * gift_filter.weight / self.total_weight
            else:
                budget = balance

            if gift_filter.max_spend_money > 0:
                budget = min(budget, gift_filter.max_spend_money)

            for gift in valid_gifts:
                buy_count = min(budget // gift.price, gift.remains)

                if buy_count == 0:
                    continue

                if gift_filter.max_buy_count > 0:
                    buy_count = min(buy_count, gift.max_buy_count)

                allocations.append(GiftAllocation(
                    gift=gift,
                    filter=gift_filter,
                    buy_amount=buy_count
                ))

        return allocations
