import random
from typing import List

import loguru

from app.core.interfaces.autobuyer import GiftProvider
from app.core.models import Gift


class FakeGiftProvider(GiftProvider):
    def __init__(self):
        self._gifts = self._generate_mock_gifts()

    @staticmethod
    def _generate_mock_gifts() -> List[Gift]:
        return [
            Gift(id=1, price=100, remains=10, supply=100, is_limited=True),
            Gift(id=2, price=4000, remains=5, supply=50, is_limited=True),
            Gift(id=3, price=500, remains=1, supply=10, is_limited=True),
            Gift(id=4, price=3000, remains=2, supply=2, is_limited=True),
            Gift(id=5, price=300, remains=999, supply=1000, is_limited=False),
        ]

    async def get_gifts(self) -> List[Gift]:
        for gift in self._gifts:
            gift.remains = max(0, gift.remains - random.randint(0, 1))
        loguru.logger.info(f'Received {len(self._gifts)} gifts')

        return self._gifts

    async def purchase(self, username: str, gift: Gift, hide_name: bool = True) -> None:
        ...
