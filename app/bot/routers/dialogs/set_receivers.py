import re

from aiogram import types, F
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import SetReceiversSG
from app.core.interfaces.repository import ReceiverRepository
from app.core.models import Receiver
from app.settings import RECEIVER_TEXT_PER_PAGE
from app.utils.formatters import paginate_text_blocks

USERNAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{4,31}$")


async def on_input_usernames(msg: types.Message, _, manager: DialogManager):
    raw = msg.text.strip()
    usernames = [u.strip().lstrip("@") for u in raw.split(",")]

    valid_usernames = []

    for username in usernames:
        if USERNAME_REGEX.fullmatch(username):
            valid_usernames.append(username)

    if not valid_usernames:
        await msg.answer("<b>⚠️ Не найдено ни одного корректного username.</b>")
        await manager.show()
        return

    display_blocks = [
        f'- <i>@{username}</i>' for username in valid_usernames
    ]
    pages = paginate_text_blocks(display_blocks, max_len=RECEIVER_TEXT_PER_PAGE, separator='\n')

    manager.dialog_data.update({
        "valid_usernames": valid_usernames,
        "receiver_pages": pages,
        "receiver_page_index": 0,
    })

    await manager.switch_to(SetReceiversSG.confirm)

    await manager.switch_to(SetReceiversSG.confirm)


@inject
async def on_confirm_set(
        call: types.CallbackQuery,
        _,
        manager: DialogManager,
        receiver_repository: FromDishka[ReceiverRepository]
):
    valid_usernames = manager.dialog_data.get("valid_usernames", [])

    receivers = await receiver_repository.get_all()
    await receiver_repository.delete(receiver_ids=[i.id for i in receivers])

    for username in valid_usernames:
        receiver = Receiver(username=username)
        await receiver_repository.save(receiver=receiver)

    await call.answer(
        f"✅ Список получателей обновлён!",
        parse_mode="HTML"
    )
    await manager.done()


async def get_paginated_receivers(dialog_manager: DialogManager, **_kwargs):
    pages = dialog_manager.dialog_data.get("receiver_pages", [])
    index = dialog_manager.dialog_data.get("receiver_page_index", 0)
    total = len(pages)

    index = max(0, min(index, total - 1))
    dialog_manager.dialog_data["receiver_page_index"] = index

    return {
        "text": pages[index] if total else "",
        "page": index + 1,
        "total": total,
        "pages": total,
    }


async def on_prev_page(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager
):
    current = manager.dialog_data.get("receiver_page_index", 0)
    total = len(manager.dialog_data.get("receiver_pages", []))
    manager.dialog_data["receiver_page_index"] = (current - 1) % total


async def on_next_page(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager
):
    current = manager.dialog_data.get("receiver_page_index", 0)
    total = len(manager.dialog_data.get("receiver_pages", []))
    manager.dialog_data["receiver_page_index"] = (current + 1) % total


set_receivers_dialog = Dialog(
    Window(
        Const("<b>✍️ Введите username'ы получателей через запятую:</b>"),
        MessageInput(on_input_usernames),
        Cancel(Const("❌ Отмена")),
        state=SetReceiversSG.input_usernames
    ),
    Window(
        Format(
            "<b>✅ Корректные username'ы:</b>\n"
            "{text}\n\n"
            "<b>💡 Данные username'ы будут установлены в качестве получателей подарков?</b>"
        ),
        Row(
            Button(
                Format("⬅️"),
                id="prev_page",
                on_click=on_prev_page,
            ),
            Button(
                Format("{page}/{total}"),
                id="current_page",
                on_click=None,
            ),
            Button(
                Format("➡️"),
                id="next_page",
                on_click=on_next_page,
            ),
            when=F["pages"] > 1,
        ),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_confirm_set),
            Cancel(Const("❌ Отмена")),
        ),
        state=SetReceiversSG.confirm,
        getter=get_paginated_receivers,
        parse_mode="HTML"
    )
)
