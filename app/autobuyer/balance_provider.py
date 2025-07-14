import random
from abc import ABC, abstractmethod
from typing import Optional

import loguru
from telethon import TelegramClient, errors
from telethon.tl import functions
from telethon.tl.types.payments import StarsStatus


class BalanceProvider(ABC):
    @abstractmethod
    async def get_balance(self) -> int: ...


class DefaultBalanceProvider(BalanceProvider):
    def __init__(self, client: TelegramClient):
        self._client = client

    async def get_balance(self) -> Optional[int]:
        balance: StarsStatus = await self._client(functions.payments.GetStarsStatusRequest(
            peer='me'
        ))
        balance = balance.balance.amount
        loguru.logger.success(f'Balance {balance}⭐️')
        return balance


class FakeBalanceProvider(BalanceProvider):
    def __init__(self):
        self._balance = random.randint(1000, 100000)
    async def get_balance(self) -> int:
        loguru.logger.success(f'Balance {self._balance}⭐️')
        return self._balance
