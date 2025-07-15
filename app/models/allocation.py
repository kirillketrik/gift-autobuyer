from pydantic import BaseModel

from .gift import Gift
from .gift_filter import GiftFilter


class GiftAllocation(BaseModel):
    filter: GiftFilter
    gift: Gift
    buy_amount: int



