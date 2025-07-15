from typing import List

from app.core.interfaces.repository import ReceiverReader, ReceiverWriter
from app.core.models import Receiver
from app.database.models.receiver import ReceiverModel


class TortoiseReceiverRepository(ReceiverReader, ReceiverWriter):
    async def get_all(self) -> List[Receiver]:
        models = await ReceiverModel.all()
        return [
            Receiver.model_validate(m) for m in models
        ]

    async def save(self, receiver: Receiver) -> None:
        model = await ReceiverModel.create(**receiver.model_dump())
        return Receiver.model_validate(model)

    async def delete(self, receiver_ids: List[int]) -> None:
        await ReceiverModel.filter(id__in=receiver_ids).delete()
