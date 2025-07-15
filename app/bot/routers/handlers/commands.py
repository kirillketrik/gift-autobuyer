from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.bot.states import MainMenuSG

router = Router()


@router.message(Command('start'))
async def start_bot(msg: types.Message, dialog_manager: DialogManager):
    await msg.answer(
        "<b>👋 Добро пожаловать!</b>\n\n"
        "Этот бот автоматически покупает подарки в Telegram по заданным фильтрам. "
        "Вы можете настраивать критерии (цена, редкость, лимиты) и указывать получателей.\n\n"
        "📦 <b>Основные возможности:</b>\n"
        "• Создание фильтров вручную или с помощью ИИ\n"
        "• Поддержка нескольких получателей подарков\n"
        "• Автоматическая покупка подарков с учётом приоритетов и бюджета\n\n"
        "<b>💡 После настройки бот начнёт отслеживать подарки и автоматически их покупать по заданным правилам.</b>",
        parse_mode="HTML",
        disable_notification=True
    )
    await dialog_manager.start(
        state=MainMenuSG.menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )
