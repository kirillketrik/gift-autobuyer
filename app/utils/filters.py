import json
from typing import Optional, List, Dict

from app.models.gift_filter import GiftFilter
from .ai import ask_ai

_SYSTEM_PROMT = """
Ты — интеллектуальный ассистент, который помогает пользователю создавать фильтры для автоматической покупки подарков в Telegram.

На основе пользовательского запроса тебе нужно вернуть список объектов JSON, каждый из которых представляет собой фильтр с конкретными параметрами.

Структура каждого фильтра строго соответствует следующей модели:

{
  "min_supply": -1,                // Минимальное доступное количество подарков (если не указано — установить -1)
  "max_supply": -1,                // Максимальное доступное количество подарков (если не указано — установить -1)
  "min_price": -1,                 // Минимальная цена подарка в звёздах (если не указано — установить -1)
  "max_price": -1,                 // Максимальная цена подарка в звёздах (если не указано — установить -1)
  "priority": 0,                   // Приоритет фильтра (чем выше, тем раньше он применяется). Диапазон 0-100
  "weight": -1,                    // Вес (в процентах) — доля от бюджета, выделяемая на подарки по этому фильтру (если не указано — -1)
  "max_buy_count": -1,            // Максимальное количество покупок по данному фильтру (если не указано — -1)
  "max_spend_money": -1           // Максимальная сумма в звёздах, которую можно потратить по фильтру (если не указано — -1)
}

⚠️ Правила:
- Верни **только список объектов** JSON-фильтров.
- Каждый фильтр должен быть валидным, с обязательными полями.
- Если в запросе пользователя явно или неявно упомянуты **несколько условий**, разбей их на **отдельные фильтры**.
- Все числовые значения должны быть целыми числами.
- Не добавляй пояснений, комментариев или описания — только JSON-массив.
- Если что-то не указано, используй значение по умолчанию: `-1` или `0`.

Примеры:
1. "Покупай дешёвые подарки до 100 звёзд" → один фильтр с `max_price: 100`.
2. "Купи редкие подарки, но только 3 штуки, не дороже 500" → фильтр с `max_price`, `max_buy_count`.

Твоя задача — анализировать смысл и разбивать его на понятные, чёткие фильтры.

Вот пользовательский запрос, который нужно проанализировать:"""


def _parse_filters(text: str) -> Optional[List[Dict]]:
    try:
        i = text.index('[')
        j = len(text) - 1

        while text[j] != ']' and j > 0:
            j -= 1

        return json.loads(text[i:j + 1])
    except ValueError:
        return None


async def parse_text_to_filters(query: str) -> Optional[List[GiftFilter]]:
    promt = _SYSTEM_PROMT + query
    response = await ask_ai(promt=promt)

    if response is None:
        return None

    filters = _parse_filters(response)

    if filters is None:
        return None

    filters = [GiftFilter(**f) for f in filters]

    return filters


def parse_name_value_line(text: str) -> List[GiftFilter]:
    default_filter = {
        "enabled": True,
        "min_price": -1,
        "max_price": -1,
        "min_supply": -1,
        "max_supply": -1,
        "priority": 0,
        "weight": -1,
        "max_buy_count": -1,
        "max_spend_money": -1
    }

    filters = []
    raw_filters = text.strip().split("\n\n")

    for raw in raw_filters:
        filter_data = default_filter.copy()
        lines = raw.strip().replace("\n", " ").split()

        for item in lines:
            if "=" not in item:
                continue
            key, value = item.split("=", 1)
            key = key.strip()
            if key not in filter_data:
                continue
            val = value.strip()
            if val.lower() in ("true", "false"):
                filter_data[key] = val.lower() == "true"
            else:
                try:
                    filter_data[key] = int(val)
                except ValueError:
                    continue

        filters.append(GiftFilter(**filter_data))

    return filters
