from typing import List

from app.core.interfaces.repository import GiftFilterReader, GiftFilterWriter
from app.core.models import GiftFilter
from app.database.models import GiftFilterModel


class TortoiseGiftFilterRepository(GiftFilterReader, GiftFilterWriter):
    async def get_all(self) -> List[GiftFilter]:
        models = await GiftFilterModel.all()
        return [
            GiftFilter.model_validate(m) for m in models
        ]

    async def save(self, gift_filter: GiftFilter) -> GiftFilter:
        model = await GiftFilterModel.create(**gift_filter.model_dump(exclude=['id']))
        return GiftFilter.model_validate(model)

    async def delete(self, filter_ids: List[int]) -> None:
        await GiftFilterModel.filter(id__in=filter_ids).delete()
