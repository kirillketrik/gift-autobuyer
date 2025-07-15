import asyncio

from app.autobuyer.exceptions import NotAuthorizedError, GiftSoldOutError, InsufficientBalanceError, FloodError, \
    NoGiftChangesError
from app.core.interfaces.autobuyer import Autobuyer, GiftProvider, BalanceProvider, Notifier, GiftAllocator
from app.core.interfaces.repository import GiftFilterReader, ReceiverReader


class DefaultAutobuyer(Autobuyer):
    async def autobuy(
            self,
            gift_filter_reader: GiftFilterReader,
            receiver_reader: ReceiverReader,
            balance_provider: BalanceProvider,
            gift_provider: GiftProvider,
            gift_allocator: GiftAllocator,
            notifier: Notifier,
    ) -> None:
        gift_filters = await gift_filter_reader.get_all()
        receivers = await receiver_reader.get_all()
        receiver_count = len(receivers)

        try:
            gifts = await gift_provider.get_gifts()

            if len(gifts) == 0: return

            balance = await balance_provider.get_balance()
            allocations = await gift_allocator.get_allocations(
                balance=balance,
                gift_filters=gift_filters,
                gifts=gifts,
            )

            if len(allocations) == 0: return

            receiver_index = 0

            for allocation in allocations:
                for _ in range(allocation.buy_amount):
                    username = receivers[receiver_index % receiver_count].username
                    try:
                        await gift_provider.purchase(
                            username=username,
                            gift=allocation.gift,
                            hide_name=True
                        )
                    except GiftSoldOutError:
                        break
                    except InsufficientBalanceError:
                        await notifier.notify(
                            message="<b>⚠️ На вашем балансе недостаточно средств! Покупка подарков невозможна!</b>"
                        )
                        return

                    await asyncio.sleep(0.444)
        except NoGiftChangesError:
            return
        except NotAuthorizedError:
            await notifier.notify(
                message='<b>⚠️ Сессия телеграмм аккаунт для автопокупки была завершена!\n\n'
                        'Для возобновления автопокупки войдите в аккаунт снова.</b>'
            )
        except FloodError as error:
            await asyncio.sleep(error.pause)
