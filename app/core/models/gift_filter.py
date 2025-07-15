from typing import Optional, Annotated

from pydantic import BaseModel, Field

from .gift import Gift


class GiftFilter(BaseModel):
    id: Annotated[Optional[int], Field(default=None, description="ID фильтра")]
    enabled: Annotated[bool, Field(default=True, description="Включен ли фильтр")]
    min_supply: Annotated[int, Field(default=-1, description="Минимальный саплай подарков. -1 = выключено")]
    max_supply: Annotated[int, Field(default=-1, description="Максимальный саплай подарка. -1 = выключено")]
    min_price: Annotated[int, Field(default=-1, description="Минимальная цена подарка. -1 = выключено")]
    max_price: Annotated[int, Field(default=-1, description="Максимальная цена подарка. -1 = выключено")]
    priority: Annotated[int, Field(default=0, description="Приоритет покупки подарков")]
    weight: Annotated[int, Field(default=-1, description="Часть бюджета для подарков. -1 = выключено")]
    max_buy_count: Annotated[int, Field(default=-1, description="Максимальное кол-во покупок. -1 = без лимита")]
    max_spend_money: Annotated[int, Field(default=-1, description="Максимально можно потратить. -1 = без лимита")]
    ordering: Annotated[str, Field(default='-price', description="Сортировка отфильтрованных результатов. Сортировка может быть по полям price и supply в убывающем или возрастающем порядке.")]

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
