import loguru
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🔄 Перезапустить бота"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())


async def on_startup(bot: Bot):
    bot_info = await bot.me()
    await set_commands(bot)
    loguru.logger.success(f'Bot successfully started @{bot_info.username}')
