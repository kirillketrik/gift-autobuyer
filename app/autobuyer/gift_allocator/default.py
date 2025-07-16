from typing import List

from app.core.interfaces.autobuyer import GiftAllocator
from app.core.models import Gift, GiftAllocation, GiftFilter


class DefaultGiftAllocator(GiftAllocator):
    async def get_allocations(
            self,
            balance: int,
            gift_filters: List[GiftFilter],
            gifts: List[Gift]
    ) -> List[GiftAllocation]:
        allocations = []

        total_weight = sum(f.weight for f in gift_filters)
        has_null_weight = any(f.weight <= 0 for f in gift_filters)

        for gift_filter in gift_filters:
            order, field = gift_filter.ordering[0], gift_filter.ordering[1:]

            valid_gifts = sorted(
                [g for g in gifts if gift_filter.match(g)],
                key=lambda g: getattr(g, field, 0),
                reverse=order == '-'
            )

            if len(valid_gifts) == 0:
                continue

            if gift_filter.weight > 0 and not has_null_weight:
                budget = balance * gift_filter.weight / total_weight
            else:
                budget = balance

            if gift_filter.max_spend_money > 0:
                budget = min(budget, gift_filter.max_spend_money)

            if balance == 0:
                break

            for gift in valid_gifts:
                buy_count = min(budget // gift.price, gift.remains)

                if gift_filter.max_buy_count > 0:
                    buy_count = min(buy_count, gift_filter.max_buy_count)

                total_price = buy_count * gift.price

                if total_price > balance:
                    buy_count = balance // gift.price
                    total_price = buy_count * gift.price

                if buy_count == 0:
                    continue

                balance -= total_price

                allocations.append(GiftAllocation(
                    gift=gift,
                    filter=gift_filter,
                    buy_amount=buy_count
                ))

        return allocations
