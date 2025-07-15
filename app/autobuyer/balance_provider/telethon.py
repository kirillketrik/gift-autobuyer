from typing import Optional

import telethon.errors
from telethon import TelegramClient
from telethon.tl import functions
from telethon.tl.types.payments import StarsStatus

from app.autobuyer.exceptions import FloodError, NotAuthorizedError
from app.core.interfaces.autobuyer import BalanceProvider


class TelethonBalanceProvider(BalanceProvider):
    def __init__(self, client: TelegramClient):
        self._client = client

    async def get_balance(self) -> Optional[int]:
        try:
            balance: StarsStatus = await self._client(functions.payments.GetStarsStatusRequest(
                peer='me'
            ))
        except telethon.errors.FloodWaitError as error:
            raise FloodError(pause=error.seconds)
        except (
                telethon.errors.AuthKeyUnregisteredError,
                telethon.errors.UserDeactivatedBanError,
        ):
            raise NotAuthorizedError()
        balance = balance.balance.amount
        return balance
