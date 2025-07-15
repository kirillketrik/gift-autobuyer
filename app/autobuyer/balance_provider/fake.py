import random

import loguru

from app.core.interfaces.autobuyer import BalanceProvider


class FakeBalanceProvider(BalanceProvider):
    def __init__(self):
        self._balance = random.randint(1000, 100000)

    async def get_balance(self) -> int:
        loguru.logger.success(f'Balance {self._balance}⭐️')
        return self._balance
