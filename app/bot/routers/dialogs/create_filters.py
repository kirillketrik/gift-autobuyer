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
from app.utils.filters import parse_text_to_filters, parse_name_value_line
from app.utils.formatters import format_filter, paginate_text_blocks


@inject
async def on_save_filters(
        _,
        __,
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
    page_index = dialog_manager.dialog_data.get("filter_page_index", 0)

    if pages is None:
        formatted_blocks = [
            format_filter(f, index=i) for i, f in enumerate(filters)
        ]
        pages = paginate_text_blocks(formatted_blocks)
        dialog_manager.dialog_data["filter_pages"] = pages

    page_index = max(0, min(page_index, len(pages) - 1))
    dialog_manager.dialog_data["filter_page_index"] = page_index
    page_info = f"<b>Страница {page_index + 1} из {len(pages)}</b>" if len(pages) > 1 else ""
    return {
        "filters_text": pages[page_index],
        "page_info": page_info,
        "pages": len(pages),
    }


async def on_prev_page(_, __, manager: DialogManager):
    manager.dialog_data["filter_page_index"] = max(0, manager.dialog_data.get("filter_page_index", 0) - 1)


async def on_next_page(_, __, manager: DialogManager):
    pages = manager.dialog_data.get("filter_pages", [])
    manager.dialog_data["filter_page_index"] = min(len(pages) - 1, manager.dialog_data.get("filter_page_index", 0) + 1)


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
        await message.answer(
            text=(
                "⚠️ <b>Упс! Что-то пошло не так.</b>\n\n"
                "Попробуйте, пожалуйста, ещё раз.\n\n"
                "Если проблема сохраняется, напишите разработчику."
            )
        )


# Парсинг вручную
async def on_manual_input(message, _, manager: DialogManager):
    try:
        filters = parse_name_value_line(text=message.text)
        manager.dialog_data["filters"] = filters
        await manager.switch_to(EditGiftFilterSG.confirm)
    except Exception:
        await message.answer(
            text=(
                "⚠️ <b>Неверный формат ввода.</b>\n\n"
                "Пожалуйста, введите фильтры в формате <code>name=value</code>, "
                "разделяя несколько фильтров двумя пустыми строками.\n\n"
                "Пример:\n"
                "<code>min_price=100 max_price=500</code>\n\n"
                "<code>priority=10 max_spend_money=1000</code>"
            )
        )


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
✍️ <b>Введите параметры фильтров вручную в формате: <code>имя=значение</code></b>

<b>- Пробел должен разделять параметры одного фильтра</b>
<b>- Две пустые строки должны разделять разные фильтры</b>

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
            "<b>🔔 Сформированы следующие фильтры:</b>\n\n{filters_text}\n\n{page_info}"
        ),
        Row(
            Button(Const("⬅️ Назад"), id="prev", on_click=on_prev_page),
            Button(Const("➡️ Далее"), id="next", on_click=on_next_page),
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
