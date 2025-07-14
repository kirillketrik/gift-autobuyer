from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🔄 Перезапустить бота"),
        BotCommand(command="create_filters", description="🛠 Создать фильтры для покупки"),
        BotCommand(command="show_filters", description="📋 Показать все фильтры"),
        BotCommand(command="delete_filters", description="🗑 Удалить фильтры по ID"),
        BotCommand(command="set_receivers", description="🎯 Установить получателей подарков"),
        BotCommand(command="show_receivers", description="📬 Показать текущих получателей"),
    ]

    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
