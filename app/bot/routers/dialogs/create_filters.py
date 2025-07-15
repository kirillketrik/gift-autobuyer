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

💡 <b>Примеры, как можно сформулировать запросы:</b>

👨 <b>Пример запроса:</b>
<code>Хочу покупать подарки с саплаем до 10000, цена от 200 до 1000 звёзд, максимум по 3 штуки каждого.</code>
🤖 <b>Результат:</b><code>
🔸 Фильтр #1
 - Цена: 200-1000
 - Саплай: до 10000
 - Макс. кол-во: 3
 - Сортировка: -price
</code>

👨 <b>Пример запроса:</b>
<code>Сделай два фильтра: первый — для подарков от 1000 звёзд и выше, с весом бюджета 40%; второй — для подарков до 300 звёзд, с весом бюджета 60% и ограничением по количеству 5 штук.</code>
🤖 <b>Результат:</b><code>
🔸 Фильтр #1
 - Цена: от 1000
 - Доля бюджета: 40
 - Сортировка: -price

🔸 Фильтр #2
 - Цена: до 300
 - Доля бюджета: 60
 - Макс. кол-во: 5
 - Сортировка: -price
</code>
"""
        ),
        MessageInput(on_ai_input),
        Back(Const("🔙 Назад")),
        state=EditGiftFilterSG.input_promt,
    ),

    Window(
        Const(
            """
✍️ <b>Введите параметры фильтров вручную в формате <code>имя=значение</code></b>
- В качестве разделителя для параметров одного фильтра используй пробел
- Чтобы создать несколько фильтров, разделяйте их двумя пустыми строками

<b>👨 Пример запроса №1:</b>
<code>min_price=1000 weight=40 ordering=-price</code>

<code>max_price=300 weight=60 max_buy_count=5 ordering=-price</code>
🤖 <b>Результат:</b>
<code>🔸 Фильтр #1
- Цена: от 1000
- Доля бюджета: 40
- Сортировка: по убыванию цены

🔸 Фильтр #2
- Цена: до 300
- Доля бюджета: 60
- Макс. кол-во: 5
- Сортировка: по убыванию цены</code>

<b>👨 Пример запроса №2:</b>
<code>min_supply=10 max_price=500 max_spend_money=2000 ordering=-price</code>
🤖 <b>Результат:</b>
<code>🔸 Фильтр #1
- Кол-во: от 10
- Цена: до 500
- Макс. трата: 2000
- Сортировка: по убыванию цены</code>
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
