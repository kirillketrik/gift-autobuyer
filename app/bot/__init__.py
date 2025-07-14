from typing import List, Dict

from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram_dialog import setup_dialogs

from app.bot.middlewares import AccessControlOuterMiddleware
from . import routers
from . import events


async def start_bot(
        bot_token: str,
        admin_ids: List[int],
        context: Dict
):
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.outer_middleware(AccessControlOuterMiddleware(allowed_user_ids=admin_ids))
    dp.include_router(routers.router)
    setup_dialogs(dp)
    dp.startup.register(events.on_startup)
    await dp.start_polling(
        bot,
        allowed_updates=['message', 'callback_query'],
        **context
    )
