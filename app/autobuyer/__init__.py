import asyncio
from loguru import logger

from app.autobuyer.exceptions import (
    NotAuthorizedError,
    GiftSoldOutError,
    InsufficientBalanceError,
    FloodError,
    NoGiftChangesError
)
from app.core.interfaces.autobuyer import GiftProvider, BalanceProvider, Notifier, GiftAllocator
from app.core.interfaces.repository import GiftFilterReader, ReceiverReader


class Autobuyer:
    def __init__(
        self,
        gift_filter_reader: GiftFilterReader,
        receiver_reader: ReceiverReader,
        balance_provider: BalanceProvider,
        gift_provider: GiftProvider,
        gift_allocator: GiftAllocator,
        notifier: Notifier,
        pause_after_buy: int,
    ):
        self.gift_filter_reader = gift_filter_reader
        self.receiver_reader = receiver_reader
        self.balance_provider = balance_provider
        self.gift_provider = gift_provider
        self.gift_allocator = gift_allocator
        self.notifier = notifier
        self.pause_after_buy = pause_after_buy

    async def autobuy(self) -> None:
        logger.info("Autobuy started.")
        gift_filters = await self.gift_filter_reader.get_all()
        receivers = await self.receiver_reader.get_all()
        receiver_count = len(receivers)

        try:
            logger.info("Fetching available gifts...")
            gifts = await self.gift_provider.get_gifts()
            if len(gifts) == 0:
                logger.info("No gifts available. Skipping autobuy.")
                return

            logger.info(f"{len(gifts)} gifts fetched.")

            balance = await self.balance_provider.get_balance()
            logger.info(f"Available balance: {balance}")

            allocations = await self.gift_allocator.get_allocations(
                balance=balance,
                gift_filters=gift_filters,
                gifts=gifts,
            )

            if len(allocations) == 0:
                logger.info("No valid allocations found. Skipping autobuy.")
                return

            logger.info(f"{len(allocations)} gift allocations generated.")

            receiver_index = 0

            for allocation in allocations:
                logger.info(f"Processing allocation: {allocation.gift.name} x{allocation.buy_amount}")
                for i in range(allocation.buy_amount):
                    username = receivers[receiver_index % receiver_count].username
                    logger.info(f"Attempting to buy gift for @{username}")

                    try:
                        await self.gift_provider.purchase(
                            username=username,
                            gift=allocation.gift,
                            hide_name=True
                        )
                        logger.success(f"Gift '{allocation.gift.name}' purchased for @{username}")
                    except GiftSoldOutError:
                        logger.warning(f"Gift '{allocation.gift.name}' is sold out. Skipping to next.")
                        break
                    except InsufficientBalanceError:
                        logger.error("Insufficient balance to continue gift purchases.")
                        await self.notifier.notify(
                            message="<b>⚠️ На вашем балансе недостаточно средств! Покупка подарков невозможна!</b>"
                        )
                        return

                    await asyncio.sleep(self.pause_after_buy)
        except NoGiftChangesError:
            logger.info("No gift changes detected. Skipping this cycle.")
            return
        except NotAuthorizedError:
            logger.error("Telegram session has expired.")
            await self.notifier.notify(
                message='<b>⚠️ Сессия телеграмм аккаунта для автопокупки была завершена!\n\n'
                        'Для возобновления автопокупки войдите в аккаунт снова.</b>'
            )
        except FloodError as error:
            logger.warning(f"Flood control triggered. Sleeping for {error.pause} seconds.")
            await asyncio.sleep(error.pause)
        except Exception as e:
            logger.exception(f"Unexpected error during autobuy: {e}")
