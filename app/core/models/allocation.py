from pydantic import BaseModel

from .gift import Gift
from .gift_filter import GiftFilter


class GiftAllocation(BaseModel):
    filter: GiftFilter
    """Применённый фильтр"""
    gift: Gift
    """Подарок прошедший фильтр"""
    buy_amount: int
    """Кол-во единиц подарка, которое будет приобретаться"""



