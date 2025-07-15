import random
from abc import ABC, abstractmethod
from typing import List

import loguru
from pydantic import ValidationError
from telethon import TelegramClient
from telethon import functions
from telethon.errors import BadRequestError
from telethon.tl import functions
from telethon.tl.types import InputInvoiceStarGift, InputPeerUser
from telethon.tl.types.payments import PaymentFormStarGift
from telethon.tl.types.payments import StarGifts

from app.autobuyer.exceptions import OldGiftsReceivedError, GiftSoldOutError, AutobuyerError
from app.models import Gift


class GiftProvider(ABC):
    @abstractmethod
    async def get_gifts(self) -> List[Gift]: ...

    @abstractmethod
    async def purchase(self, username: str, gift: Gift, hide_name: bool = True) -> bool: ...


class DefaultGiftProvider(GiftProvider):
    def __init__(self, client: TelegramClient):
        self._client = client
        self._peers = {}
        self._lash_gifts_hash = None

    async def _get_peer(self, username: str) -> InputPeerUser:
        peer = self._peers.get(username)
        if peer is None:
            peer = await self._client.get_input_entity(peer=username)
            self._peers[username] = peer
        return peer

    async def get_gifts(self) -> List[Gift]:
        response: StarGifts = await self._client(
            functions.payments.GetStarGiftsRequest(hash=0)
        )
        if response.hash == self._lash_gifts_hash:
            raise OldGiftsReceivedError()
        else:
            self._lash_gifts_hash = response.hash

        gifts: List[Gift] = []

        for gift in response.gifts:
            try:
                gift = Gift(
                    id=gift.id,
                    price=gift.stars,
                    supply=gift.availability_total,
                    remains=gift.availability_remains,
                    is_limited=gift.limited
                )
            except ValidationError:
                continue
            if gift.is_limited:
                gifts.append(gift)

        loguru.logger.success(f'Received {len(gifts)} gifts')

        return gifts

    async def purchase(self, username: str, gift: Gift, hide_name: bool = True) -> bool:
        loguru.logger.info(f'Purchasing gift {gift} for @{username}')
        try:
            peer = await self._get_peer(username=username)
            invoice = InputInvoiceStarGift(
                peer=peer,
                gift_id=gift.id,
                hide_name=hide_name
            )
            form: PaymentFormStarGift = await self._client(
                functions.payments.GetPaymentFormRequest(
                    invoice=invoice
                )
            )
            await self._client(
                functions.payments.SendStarsFormRequest(
                    form_id=form.form_id,
                    invoice=invoice,
                )
            )
            loguru.logger.success('Gift purchased successfully')
        except BadRequestError as e:
            error = str(e.message)
            if 'STARGIFT_USAGE_LIMITED' in error:
                raise GiftSoldOutError()
            else:
                raise AutobuyerError(error)


class FakeGiftProvider(GiftProvider):
    def __init__(self):
        self._gifts = self._generate_mock_gifts()

    @staticmethod
    def _generate_mock_gifts() -> List[Gift]:
        return [
            Gift(id=1, price=100, remains=10, supply=100, is_limited=True),
            Gift(id=2, price=4000, remains=5, supply=50, is_limited=True),
            Gift(id=3, price=500, remains=1, supply=10, is_limited=True),
            Gift(id=4, price=3000, remains=2, supply=2, is_limited=True),
            Gift(id=5, price=300, remains=999, supply=1000, is_limited=False),
        ]

    async def get_gifts(self) -> List[Gift]:
        for gift in self._gifts:
            gift.remains = max(0, gift.remains - random.randint(0, 1))
        loguru.logger.info(f'Received {len(self._gifts)} gifts')

        return self._gifts

    async def purchase(self, username: str, gift: Gift, hide_name: bool = True) -> bool:
        loguru.logger.success(f"Purchase gift {gift} for @{username}")
        return True  # Всегда успешная покупка
