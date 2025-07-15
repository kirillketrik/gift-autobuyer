import re

from aiogram import types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row
from aiogram_dialog.widgets.text import Const, Jinja

from app.bot.states import SetReceiversSG
from app.core.interfaces.repository import ReceiverRepository
from app.core.models import Receiver

USERNAME_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{4,31}$")


async def on_input_usernames(msg: types.Message, _, manager: DialogManager):
    raw = msg.text.strip()
    usernames = [u.strip().lstrip("@") for u in raw.split(",")]

    valid_usernames = []
    invalid_usernames = []

    for username in usernames:
        if USERNAME_REGEX.fullmatch(username):
            valid_usernames.append(username)
        else:
            invalid_usernames.append(username)

    if not valid_usernames:
        await msg.answer("⚠️ Не найдено ни одного корректного username. Попробуйте снова.")
        return

    manager.dialog_data["valid_usernames"] = valid_usernames
    manager.dialog_data["display_valid_usernames"] = [f'@{u}' for u in valid_usernames]
    manager.dialog_data["invalid_usernames"] = invalid_usernames

    await manager.switch_to(SetReceiversSG.confirm)


async def on_confirm_set(c: types.CallbackQuery, _, manager: DialogManager):
    valid_usernames = manager.dialog_data.get("valid_usernames", [])

    receiver_repository: ReceiverRepository = manager.dialog_data.get("receiver_repository")
    receivers = await receiver_repository.get_all()
    await receiver_repository.delete(receiver_ids=[i.id for i in receivers])

    for username in valid_usernames:
        receiver = Receiver(username=username)
        await receiver_repository.save(receiver=receiver)

    await c.message.answer(
        f"✅ Обновлён список получателей:\n\n" +
        "\n".join(f"• @{u}" for u in valid_usernames),
        parse_mode="HTML"
    )
    await manager.done()


set_receivers_dialog = Dialog(
    Window(
        Const("Введите username'ы получателей через запятую:\n\n"
              "Пример: <code>user1,user2,user3</code>"),
        MessageInput(on_input_usernames),
        Cancel(Const("❌ Отмена")),
        state=SetReceiversSG.input_usernames
    ),
    Window(
        Jinja(
            "✅ Корректные username'ы:\n{{','.join(dialog_data['display_valid_usernames'])}}\n\n"
            "{% if dialog_data['invalid_usernames'] %}"
            "⚠️ <b>Некорректные username'ы:</b>\n{{','.join(dialog_data['invalid_usernames'])}}\n\n"
            "{% endif %}"
            "Список корретных username'ов будет установлен в качестве получателей?"
        ),
        Row(
            Button(Const("✅ Подтвердить"), id="confirm", on_click=on_confirm_set),
            Cancel(Const("❌ Отмена")),
        ),
        state=SetReceiversSG.confirm
    )
)
