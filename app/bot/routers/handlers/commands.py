from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.bot.states import EditGiftFilterSG, DeleteFilterSG, SetReceiversSG, MainMenuSG, AuthSG
from app.database.models import GiftFilterModel
from app.models import GiftFilter
from app.utils.formatters import format_filter, paginate_text_blocks

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
        "⚙️ <b>Команды для управления:</b>\n"
        "<code>/create_filters</code> — создать фильтры для покупки\n"
        "<code>/show_filters</code> — показать список текущих фильтров\n"
        "<code>/delete_filters</code> — удалить фильтры по ID\n\n"
        "<code>/set_receivers user1,user2</code> — указать получателей подарков\n"
        "<code>/show_receivers</code> — показать список получателей\n\n"
        "💡 После настройки бот начнёт отслеживать подарки и автоматически их покупать по заданным правилам.",
        parse_mode="HTML"
    )
    await dialog_manager.start(
        state=MainMenuSG.menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )


@router.message(Command('show_filters'))
async def show_filters(msg: types.Message):
    filters = await GiftFilterModel.all().order_by("id")

    if not filters:
        await msg.answer("<b>⚠️ У вас пока нет ни одного фильтра.</b>")
        return

    texts = [format_filter(GiftFilter.model_validate(f)) for f in filters]
    blocks = paginate_text_blocks(texts)
    for index, block in enumerate(blocks):
        text = f"<b>📑 Страница {index + 1}/{len(blocks)}</b>\n\n" + block
        await msg.answer(text)


@router.message(Command('create_filters'))
async def edit_filters(_, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=EditGiftFilterSG.select_mode,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )




@router.message(Command('delete_filters'))
async def start_delete_filters(_, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=DeleteFilterSG.input_ids,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )


@router.message(Command("set_receivers"))
async def start_set_receivers_dialog(_, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=SetReceiversSG.input_usernames,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )

@router.message(Command('auth'))
async def edit_filters(_, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=AuthSG.phone,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )