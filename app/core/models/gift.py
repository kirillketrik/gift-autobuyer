from typing import Annotated

from pydantic import BaseModel, Field


class Gift(BaseModel):
    id: int
    """
    Уникальный идентификатор подарка. Используется при покупке и для отслеживания.
    """

    price: Annotated[int, Field(gt=0)]
    """
    Стоимость подарка в звёздах (stars).
    """

    remains: Annotated[int, Field(gt=0)]
    """
    Текущее доступное количество (остаток) подарков.
    Используется для ограничения количества при покупке.
    """

    supply: Annotated[int, Field(gt=0)]
    """
    Общий тираж подарка (если известен). Используется для фильтрации в правилах (например, rare < 1000).
    """

    is_limited: bool = False
    """
    Признак лимитированного подарка (True, если supply/remains ограничены).
    Используется для более тонкой фильтрации или отображения в UI.
    Может быть None, если информация отсутствует.
    """

    def __str__(self):
        return f'{self.price}⭐️'
