from typing import List

from aiogram import Bot
from aiogram.enums import ParseMode

from app.core.interfaces.autobuyer import Notifier


class TelegramNotifier(Notifier):
    def __init__(self, token: str, user_ids: List[int]):
        self.bot = Bot(token)
        self.user_ids = user_ids

    async def notify(self, message: str) -> None:
        for user_id in self.user_ids:
            try:
                await self.bot.send_message(
                    chat_id=user_id,
                    parse_mode=ParseMode.HTML,
                    text=message
                )
            except Exception:
                pass
