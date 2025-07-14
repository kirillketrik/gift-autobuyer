import loguru
from aiogram import Bot

from app.bot.misc import set_commands


async def on_startup(bot: Bot):
    bot_info = await bot.me()
    await set_commands(bot)
    loguru.logger.success(f'Bot successfully started @{bot_info.username}')
