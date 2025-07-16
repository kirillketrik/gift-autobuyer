from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.bot.states import MainMenuSG

router = Router()


@router.message(Command('start'))
async def start_bot(msg: types.Message, dialog_manager: DialogManager):
    await msg.answer(
        "<b>👋 Добро пожаловать в Telegram Gift Autobuyer!</b>\n\n"
        "Этот бот автоматически покупает подарки в Telegram по заданным вами фильтрам.\n"
        "Вы можете точно управлять тем, какие подарки покупать, кому их отправлять и сколько тратить.\n\n"
        "📦 <b>Что умеет бот:</b>\n"
        "• Создание фильтров вручную (через параметры) или с помощью ИИ-запросов\n"
        "• Поддержка нескольких получателей (юзеры и каналы)\n"
        "• Учёт цены, редкости, лимитов на количество и бюджет\n"
        "• Приоритеты, весовая доля бюджета и продвинутая сортировка подарков\n\n"
        "🔧 <b>Как это работает:</b>\n"
        "1. Вы задаёте фильтры — что покупать и на каких условиях\n"
        "2. Назначаете получателей\n"
        "3. Бот отслеживает доступные подарки и покупает подходящие — автоматически\n\n"
        "💡 Всё управление осуществляется через удобное меню. Начнём!",
        parse_mode="HTML",
        disable_notification=True
    )
    await dialog_manager.start(
        state=MainMenuSG.menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )
