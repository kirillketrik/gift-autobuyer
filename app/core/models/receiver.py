from pydantic import BaseModel


class Receiver(BaseModel):
    username: str
