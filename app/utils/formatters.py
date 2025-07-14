from app.models import GiftFilter


def format_filter(data: GiftFilter, index: int = 0) -> str:
    FIELD_NAMES = {
        "min_price": "Мин. цена",
        "max_price": "Макс. цена",
        "min_supply": "Мин. саплай",
        "max_supply": "Макс. саплай",
        "priority": "Приоритет",
        "weight": "Вес (доля бюджета)",
        "max_buy_count": "Макс. кол-во покупок",
        "max_spend_money": "Макс. бюджет",
    }

    filter_id = data.id or index + 1

    lines = [f"<b>🔸 Фильтр #{filter_id}</b>"]

    fields = {}

    if data.min_price > 0 and data.max_price > 0:
        fields['Цена'] = f'{data.min_price}-{data.max_price}'
    elif data.min_price > 0:
        fields['Цена'] = f'от {data.min_price}'
    elif data.max_price > 0:
        fields['Цена'] = f'до {data.max_price}'

    if data.min_supply > 0 and data.max_supply > 0:
        fields['Саплай'] = f'{data.min_supply}-{data.max_supply}'
    elif data.min_supply > 0:
        fields['Саплай'] = f'от {data.min_supply}'
    elif data.max_supply > 0:
        fields['Саплай'] = f'до {data.max_supply}'

    fields['Приоритет'] = data.priority
    fields['Доля бюджета'] = data.weight
    fields['Макс. кол-во'] = data.max_buy_count
    fields['Макс. бюджет'] = data.max_spend_money
    fields['Сортировка'] = data.ordering

    for label, value in fields.items():
        if isinstance(value, int) and value == -1:
            continue
        lines.append(f"<b> - {label}:</b> <code>{value}</code>")

    return "\n".join(lines)


def paginate_text_blocks(texts: list[str], max_len: int = 3500) -> list[str]:
    pages = []
    current = ""

    for block in texts:
        if len(current) + len(block) + 2 > max_len:
            pages.append(current.strip())
            current = block + "\n\n"
        else:
            current += block + "\n\n"

    if current.strip():
        pages.append(current.strip())

    return pages
