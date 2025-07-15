from typing import Optional

from pydantic import BaseModel


class Receiver(BaseModel):
    id: Optional[int] = None
    username: str
