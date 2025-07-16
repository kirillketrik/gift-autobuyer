from aiogram import types, F
from aiogram_dialog import Dialog, Window
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, Cancel, Back, SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from app.bot.states import EditGiftFilterSG
from app.core.interfaces.repository import GiftFilterRepository
from app.settings import FILTER_TEXT_PER_PAGE
from app.utils.filters import parse_text_to_filters, parse_name_value_line
from app.utils.formatters import format_filter, paginate_text_blocks


async def on_select_mode(callback: types.CallbackQuery, _, manager: DialogManager):
    mode = callback.data
    if mode == "ai":
        await manager.switch_to(EditGiftFilterSG.input_promt)
    elif mode == "manual":
        await manager.switch_to(EditGiftFilterSG.input_manually)


async def on_ai_input(message: types.Message, _, manager: DialogManager):
    await message.answer(
        text=(
            "⏳ <b>Пожалуйста, подождите...</b>\n\n"
            "ИИ анализирует ваш запрос и формирует фильтры.\n"
            "Это займёт менее 30 секунд."
        )
    )

    filters = await parse_text_to_filters(query=message.text)

    if filters:
        manager.dialog_data["filters"] = filters
        await manager.switch_to(EditGiftFilterSG.confirm)
    else:
        await message.reply(
            text=(
                "⚠️ <b>Упс! Что-то пошло не так. Попробуйте, пожалуйста, ещё раз.</b>\n\n"
                "<i>Если проблема сохраняется, напишите разработчику.</i>"
            )
        )


# Парсинг вручную
async def on_manual_input(message, _, manager: DialogManager):
    try:
        filters = parse_name_value_line(text=message.text)
        manager.dialog_data["filters"] = filters
        await manager.switch_to(EditGiftFilterSG.confirm)
    except Exception:
        await message.reply(
            text="⚠️ <b>Неверный формат ввода!</b>"
        )


@inject
async def on_save_filters(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager,
        gift_filter_repository: FromDishka[GiftFilterRepository]
):
    filters = manager.dialog_data.get("filters", [])

    for data in filters:
        await gift_filter_repository.save(data)

    await manager.done()


async def get_paginated_filters(dialog_manager: DialogManager, **_kwargs):
    filters = dialog_manager.dialog_data.get("filters", [])
    pages = dialog_manager.dialog_data.get("filter_pages")
    if pages is None:
        formatted_blocks = [
            format_filter(f, index=i) for i, f in enumerate(filters)
        ]
        pages = paginate_text_blocks(formatted_blocks, max_len=FILTER_TEXT_PER_PAGE)
        dialog_manager.dialog_data["filter_pages"] = pages

    total = len(pages)
    index = dialog_manager.dialog_data.get("filter_page_index", 0)
    index = max(0, min(index, total - 1))
    dialog_manager.dialog_data["filter_page_index"] = index

    return {
        "filters_text": pages[index],
        "page": index + 1,
        "total": total,
        "pages": total,
    }


async def on_prev_page(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager
):
    current = manager.dialog_data.get("filter_page_index", 0)
    total = len(manager.dialog_data.get("filter_pages", []))
    manager.dialog_data["filter_page_index"] = (current - 1) % total


async def on_next_page(
        _call: types.CallbackQuery,
        _button: Button,
        manager: DialogManager
):
    current = manager.dialog_data.get("filter_page_index", 0)
    total = len(manager.dialog_data.get("filter_pages", []))
    manager.dialog_data["filter_page_index"] = (current + 1) % total


# Диалог
dialog = Dialog(
    Window(
        Const("<b>💡 Выберите способ создания фильтров:</b>"),
        Row(
            Button(Const("🧠 С помощью ИИ"), id="ai", on_click=on_select_mode),
            Button(Const("✍️ Вручную (name=value)"), id="manual", on_click=on_select_mode),
        ),
        Cancel(Const("❌ Отмена")),
        state=EditGiftFilterSG.select_mode,
    ),
    Window(
        Const(
            """
<b>🧠 Опишите, какие фильтры вы хотите создать.</b>

<i> Примеры находятся в README.md файле в <b>главе 2.2.4</b></i>
"""
        ),
        MessageInput(on_ai_input),
        Back(Const("🔙 Назад")),
        state=EditGiftFilterSG.input_promt,
    ),

    Window(
        Const(
            """
✍️ <b>Введите параметры фильтров вручную, вот основные правила:</b>
1. Формат параметров должен быть: <code>имя=значение</code> 
2. Пробел должен разделять параметры одного фильтра
3. Две пустые строки должны разделять разные фильтры

<i> Примеры находятся в README.md файле в <b>главе 2.2.5</b></i>
"""),
        MessageInput(on_manual_input),
        SwitchTo(
            Const("🔙 Назад"),
            id='to_select_mode',
            state=EditGiftFilterSG.select_mode,
        ),
        state=EditGiftFilterSG.input_manually,
    ),
    Window(
        Format(
            "<b>🔔 Сформированы следующие фильтры:</b>\n\n"
            "{filters_text}\n\n"
            "<b>💡 Хотите сохранить данные фильтры?</b>"
        ),
        Row(
            Button(
                Format("⬅️"),
                id="prev",
                on_click=on_prev_page,
            ),
            Button(
                Format("{page}/{total}"),
                id="current_page",
                on_click=None
            ),
            Button(
                Format("➡️"),
                id="next",
                on_click=on_next_page,
            ),
            when=F['pages'] > 1
        ),
        Row(
            Button(Const("✅ Сохранить"), id="save", on_click=on_save_filters),
            Cancel(Const("❌ Отмена")),
        ),
        getter=get_paginated_filters,
        state=EditGiftFilterSG.confirm,
    )

)
