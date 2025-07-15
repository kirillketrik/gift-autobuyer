from typing import Optional

from pydantic import BaseModel


class Receiver(BaseModel):
    id: Optional[int] = None
    """ID получателя"""
    username: str
    """Телеграмм username получателя подарков"""

    class Config:
        from_attributes = True
