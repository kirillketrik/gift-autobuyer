from aiogram import types
from aiogram_dialog import Dialog, Window
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import DeleteFilterSG
from app.core.interfaces.repository import GiftFilterRepository


@inject
async def on_input_ids(
        msg: types.Message,
        _,
        manager: DialogManager,
        gift_filter_repository: FromDishka[GiftFilterRepository],
):
    text = msg.text.strip()
    try:
        ids = [int(x.strip()) for x in text.split(",") if x.strip().isdigit()]
    except ValueError:
        await msg.answer("❌ Ошибка при разборе ID. Убедитесь, что вы указали только числа через запятую.")
        return

    if not ids:
        await msg.answer("⚠️ Вы не указали ни одного корректного ID.")
        return

    filters = [i.id for i in await gift_filter_repository.get_all()]

    ids = [i for i in ids if i in filters]

    if len(ids) == 0:
        await msg.answer("⚠️ Фильтры с указанными ID не найдены.")
        return

    manager.dialog_data["ids"] = ids
    manager.dialog_data["display_ids"] = ",".join(str(i) for i in ids)
    await manager.switch_to(DeleteFilterSG.confirm)


@inject
async def on_confirm_delete(
        call: types.CallbackQuery,
        _,
        manager: DialogManager,
        gift_filter_repository: FromDishka[GiftFilterRepository]
):
    ids = manager.dialog_data.get("ids", [])
    await gift_filter_repository.delete(filter_ids=ids)
    await call.message.answer(f"🗑️ Удалено фильтров: <b>{len(ids)}</b>", parse_mode="HTML")
    await manager.done()


delete_filters_dialog = Dialog(
    Window(
        Const("Введите ID фильтров через запятую.\n\nПример:\n<code>1,2,3</code>"),
        MessageInput(on_input_ids),
        Cancel(Const("❌ Отмена")),
        state=DeleteFilterSG.input_ids,
        parse_mode="HTML"
    ),
    Window(
        Format("Вы действительно хотите удалить фильтры с ID: <code>{dialog_data[display_ids]}</code>?\n\n"),
        Row(
            Button(Const("✅ Да, удалить"), id="confirm", on_click=on_confirm_delete),
            Cancel(Const("❌ Отмена"))
        ),
        state=DeleteFilterSG.confirm
    )
)
