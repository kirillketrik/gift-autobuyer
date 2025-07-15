from typing import List

import telethon.errors
from pydantic import ValidationError
from telethon import TelegramClient
from telethon import functions
from telethon.tl.types import InputInvoiceStarGift, InputPeerUser
from telethon.tl.types.payments import PaymentFormStarGift
from telethon.tl.types.payments import StarGifts

from app.autobuyer.exceptions import (
    NotAuthorizedError,
    NoGiftChangesError,
    InvalidUsernameError,
    GiftSoldOutError,
    BaseGiftProviderError, FloodError
)
from app.core.interfaces.autobuyer import GiftProvider
from app.core.models import Gift


class TelethonGiftProvider(GiftProvider):
    def __init__(self, client: TelegramClient):
        self._client = client
        self._peers = {}
        self._lash_gifts_hash = None

    async def _get_peer(self, username: str) -> InputPeerUser:
        peer = self._peers.get(username)
        if peer is None:
            try:
                peer = await self._client.get_input_entity(peer=username)
            except (
                    telethon.errors.AuthKeyUnregisteredError,
                    telethon.errors.UserDeactivatedBanError,
            ):
                raise NotAuthorizedError()
            except telethon.errors.UsernameNotOccupiedError:
                raise InvalidUsernameError()
            except telethon.errors.FloodWaitError as error:
                raise FloodError(pause=error.seconds)
            self._peers[username] = peer
        return peer

    async def get_gifts(self) -> List[Gift]:
        try:
            response: StarGifts = await self._client(
                functions.payments.GetStarGiftsRequest(hash=0)
            )
        except (
                telethon.errors.AuthKeyUnregisteredError,
                telethon.errors.UserDeactivatedBanError,
        ):
            raise NotAuthorizedError()
        except telethon.errors.FloodWaitError as error:
            raise FloodError(pause=error.seconds)

        if response.hash == self._lash_gifts_hash:
            raise NoGiftChangesError()
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

        return gifts

    async def purchase(self, username: str, gift: Gift, hide_name: bool = True) -> bool:
        peer = await self._get_peer(username=username)
        invoice = InputInvoiceStarGift(
            peer=peer,
            gift_id=gift.id,
            hide_name=hide_name
        )
        try:
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
        except (
                telethon.errors.AuthKeyUnregisteredError,
                telethon.errors.UserDeactivatedBanError,
        ):
            raise NotAuthorizedError()
        except telethon.errors.FloodWaitError as error:
            raise FloodError(pause=error.seconds)
        except telethon.errors.BadRequestError as error:
            error = str(error.message)
            if 'STARGIFT_USAGE_LIMITED' in error:
                raise GiftSoldOutError()
            else:
                raise BaseGiftProviderError(error)
