from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Group, Start, Row
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import (
    SetReceiversSG,
    MainMenuSG, GiftFilterSG, ReceiverSG,
)
from app.core.interfaces.repository import ReceiverRepository


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
        Const(
            "🏠 <b>Главное меню</b>\n\n"
            "⚠️ <i>Перед использованием обязательно прочитайте <b>главу 2</b> в <a href='https://gist.github.com/kirillketrik/03c0e5419df7e3958f42a5fb752fd6a2'><b>гайде (кликабельно)</b></a></i>"
        ),
        Group(
            Start(Const("💎 Фильтры"), id="filters", state=GiftFilterSG.menu),
            Start(Const("👤 Получатели"), id="receivers", state=ReceiverSG.menu),
        ),
        state=MainMenuSG.menu,
        disable_web_page_preview=True
    )
)
