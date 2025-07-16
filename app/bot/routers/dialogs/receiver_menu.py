from aiogram import F, types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, Start, Cancel
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import SetReceiversSG, ReceiverSG
from app.core.interfaces.repository import ReceiverRepository
from app.settings import RECEIVER_TEXT_PER_PAGE
from app.utils.formatters import paginate_text_blocks


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
async def get_receiver_data(
        dialog_manager: DialogManager,
        receiver_repository: FromDishka[ReceiverRepository],
        **_kwargs
):
    receivers = await receiver_repository.get_all()
    usernames = [f"• <i>@{r.username}</i>" for r in receivers]
    pages = paginate_text_blocks(usernames, max_len=RECEIVER_TEXT_PER_PAGE)
    page = dialog_manager.dialog_data.get("page", 1)
    total = len(pages)
    page = max(min(total, page), 1)

    dialog_manager.dialog_data["page"] = page
    dialog_manager.dialog_data["total"] = total

    text = pages[page - 1] if total > 0 else ""
    return {
        "text": text,
        "total": total,
        "page": page,
        "next_page": page + 1,
        "prev_page": page - 1,
    }


receivers_dialog = Dialog(
    Window(
        Format(
            "👤 <b>Получатели подарков</b>\n\n"
            "{text}",
            when=F['total'] > 0
        ),
        Const(
            "<b>📭 Список получателей пуст</b>",
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
            Start(Const("📝 Редактировать"), id="edit_receivers", state=SetReceiversSG.input_usernames),
        ),
        Row(
            Cancel(Const("« Назад"), id="back_main")
        ),
        state=ReceiverSG.menu,
        getter=get_receiver_data,
        parse_mode="HTML"
    )
)
