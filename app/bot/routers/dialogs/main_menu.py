from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Group, Start, Row
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import (
    EditGiftFilterSG,
    SetReceiversSG,
    DeleteFilterSG, MainMenuSG,
)
from app.core.interfaces.repository import GiftFilterRepository, ReceiverRepository
from app.utils.formatters import format_filter, paginate_text_blocks


@inject
async def on_show_filters(
        call: types.CallbackQuery,
        _,
        manager: DialogManager,
        gift_filter_repository: FromDishka[GiftFilterRepository]
):
    filters = await gift_filter_repository.get_all()

    if not filters:
        await call.message.answer("⚠️ У вас пока нет ни одного фильтра.")
        return

    texts = [format_filter(f) for f in filters]
    blocks = paginate_text_blocks(texts)
    if len(blocks) == 1:
        text = f"🧾 <b>Ваши фильтры:</b>\n\n" + blocks[0]
        await call.message.answer(text, parse_mode="HTML")
    else:
        for index, block in enumerate(blocks):
            text = f"🧾 <b>Ваши фильтры — страница {index + 1}/{len(blocks)}</b>\n\n" + block
            await call.message.answer(text, parse_mode="HTML")
    await manager.show(show_mode=ShowMode.SEND)


@inject
async def on_show_receivers(
        call: types.CallbackQuery,
        _,
        manager: DialogManager,
        receiver_repository: FromDishka[ReceiverRepository]
):
    receivers = await receiver_repository.get_all()
    if not receivers:
        await call.message.answer("📭 Список получателей пуст.")
        return

    lines = ["🎁 <b>Получатели подарков:</b>"]
    for receiver in receivers:
        lines.append(f"• @{receiver.username}")
    await call.message.answer("\n".join(lines), parse_mode="HTML")
    await manager.show(show_mode=ShowMode.SEND)


main_menu_dialog = Dialog(
    Window(
        Const("🏠 <b>Главное меню</b>\n\nВыберите, что вы хотите сделать:"),
        Group(
            Button(
                Const("💎 Фильтры 💎"),
                id='show_filters',
                on_click=on_show_filters
            ),
            Row(
                Start(Const("➕ Создать"), id="create_filters", state=EditGiftFilterSG.select_mode),
                Button(Const("👁 Показать"), id="show_filters", on_click=on_show_filters),
            ),
            Row(
                Start(Const("🗑️ Удалить"), id="delete", state=DeleteFilterSG.input_ids),
            ),
            Button(
                Const("\t"),
                id='none'
            ),
            Button(
                Const("👤 Получатели 👤"),
                id='show_receivers',
                on_click=on_show_receivers
            ),
            Row(
                Start(Const("📝 Редактировать"), id="set_receivers", state=SetReceiversSG.input_usernames),
                Button(Const("👁 Показать"), id="show_receivers", on_click=on_show_receivers),
            ),
        ),
        state=MainMenuSG.menu,
        parse_mode="HTML"
    )
)
