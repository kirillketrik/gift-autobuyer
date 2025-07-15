from typing import Optional, Annotated

from pydantic import BaseModel, Field

from .gift import Gift


class GiftFilter(BaseModel):
    id: Optional[int] = None
    """ID фильтра"""
    enabled: bool = True
    """Включен ли фильтр"""
    min_supply: int = -1
    """Минимальный саплай подарка"""
    max_supply: int = -1
    """Максимальный саплай подарка"""
    min_price: int = -1
    """Минимальная цена подарка"""
    max_price: int = -1
    """Максимальная цена подарка"""
    priority: int = -1
    """Приоритет фильтра над остальными"""
    weight: int = -1
    """Доля бюджета выделенная на подарки, попадающие под данный фильтр"""
    max_buy_count: int = -1
    """Максимальное кол-во покупки для каждого отфильтрованного подарка"""
    max_spend_money: int = -1
    """Максимальное кол-во звёзд, которое будет потрачено на каждый отфильтрованный подарок"""
    ordering: str = "-price"
    """
    Сортирует отфильтрованные подарки по указанному полю и указанном порядке.
    Доступные поля для фильтрации: price, supply.
    """

    class Config:
        from_attributes = True

    def match(self, gift: Gift) -> bool:
        if not gift.supply or not gift.price:
            return True
        if self.min_supply > 0 and gift.supply < self.min_supply >= 0:
            return False
        if self.max_supply > 0 and 0 <= self.max_supply < gift.supply:
            return False
        if self.min_price > 0 and gift.price < self.min_price >= 0:
            return False
        if self.max_price > 0 and 0 <= self.max_price < gift.price:
            return False
        return True
