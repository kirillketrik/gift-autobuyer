from aiogram import F
from aiogram import types
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.kbd import Row, Start, Cancel
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import EditGiftFilterSG, DeleteFilterSG, GiftFilterSG
from app.core.interfaces.repository import GiftFilterRepository
from app.settings import FILTER_TEXT_PER_PAGE
from app.utils.formatters import format_filter, paginate_text_blocks


@inject
async def on_prev_page(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager
):
    current_page = manager.dialog_data.get("page", 1)
    total_pages = manager.dialog_data.get("total", 1)
    if current_page > 1:
        manager.dialog_data["page"] = current_page - 1
    elif current_page == 1:
        manager.dialog_data["page"] = total_pages
    await manager.answer_callback()


@inject
async def on_next_page(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager
):
    current_page = manager.dialog_data.get("page", 1)
    total_pages = manager.dialog_data.get("total", 1)
    if current_page < total_pages:
        manager.dialog_data["page"] = current_page + 1
    elif current_page == total_pages:
        manager.dialog_data["page"] = 1
    await manager.answer_callback()


@inject
async def get_filter_data(
        dialog_manager: DialogManager,
        gift_filter_repository: FromDishka[GiftFilterRepository],
        **_kwargs
):
    filters = await gift_filter_repository.get_all()
    texts = [format_filter(f) for f in filters]
    pages = paginate_text_blocks(texts, max_len=FILTER_TEXT_PER_PAGE)
    page = dialog_manager.dialog_data.get("page", 1)
    total = len(pages)
    page = max(min(total, page), 1)

    dialog_manager.dialog_data["page"] = page
    dialog_manager.dialog_data["total"] = total

    text = pages[page - 1]
    return {
        "text": text,
        "total": total,
        "page": page,
        "next_page": page + 1,
        "prev_page": page - 1,
    }


filter_dialog = Dialog(
    Window(
        Format(
            "💎 <b>Фильтры подарков</b>\n\n"
            "{text}",
            when=F['total'] > 0
        ),
        Const(
            "<b>❌ Вы ещё не добавили ни одного фильтра</b>",
            when=F['total'] == 0
        ),
        Row(
            Button(
                Format("⬅️"),
                id="prev_page",
                on_click=on_prev_page,
            ),
            Button(Format('{page}/{total}'), id='none'),
            Button(
                Format("➡️"),
                id="next_page",
                on_click=on_next_page,
            ),
            when=F['total'] > 1
        ),
        Row(
            Start(Const("➕ Создать"), id="create_filters", state=EditGiftFilterSG.select_mode),
            Start(Const("🗑️ Удалить"), id="delete_filters", state=DeleteFilterSG.input_ids),
        ),
        Row(
            Cancel(Const("« Назад"), id="back_main")
        ),
        state=GiftFilterSG.menu,
        getter=get_filter_data,
        parse_mode="HTML"
    )
)
