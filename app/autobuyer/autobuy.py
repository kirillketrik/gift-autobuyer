import asyncio
from typing import List

import loguru
from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.asyncio import BaseScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telethon import TelegramClient, errors
from telethon.errors import AuthKeyUnregisteredError

from app.autobuyer.balance_provider import BalanceProvider, DefaultBalanceProvider
from app.autobuyer.exceptions import AutobuyerError
from app.autobuyer.gift_allocator import GiftAllocator, DefaultGiftAllocator
from app.autobuyer.gift_provider import GiftProvider, DefaultGiftProvider
from app.autobuyer.notifier import Notifier, TelegramNotifier
from app.database.models import GiftFilterModel, GiftReceiverModel
from app.models import GiftFilter
from app.settings import AppConfig


async def autobuy(
        bprovider: BalanceProvider,
        gprovider: GiftProvider,
        config: AppConfig,
        notifier: Notifier,
):
    gift_filters: List[GiftFilterModel] = await (GiftFilterModel
                                                 .all()
                                                 .order_by("-priority"))
    gift_filters = [GiftFilter.model_validate(g) for g in gift_filters]

    receiver_usernames: List[str] = await (GiftReceiverModel
                                           .all()
                                           .order_by("id")
                                           .values_list("username", flat=True))
    receiver_count = len(receiver_usernames)
    allocator: GiftAllocator = DefaultGiftAllocator(gift_filters=gift_filters)
    try:
        gifts = await gprovider.get_gifts()

        if len(gifts) == 0:
            return

        balance = await bprovider.get_balance()
        allocations = allocator.get_allocations(
            balance=balance,
            gifts=gifts,
        )

        if len(allocations) == 0:
            return

        receiver_index = 0

        for allocation in allocations:
            for _ in range(allocation.buy_amount):
                try:
                    await gprovider.purchase(
                        username=receiver_usernames[receiver_index % receiver_count],
                        gift=allocation.gift
                    )
                    await asyncio.sleep(config.pause.after_buy)
                except AutobuyerError as e:
                    loguru.logger.error(e.message)

    except AutobuyerError as e:
        loguru.logger.error(e.message)
    except (errors.FloodWaitError, errors.FloodPremiumWaitError) as e:
        loguru.logger.error(f'Flood error: sleep {e.seconds}s')
        await asyncio.sleep(e.seconds)
    except (ConnectionError, AuthKeyUnregisteredError):
        await notifier.notify(
            message='<b>⚠️ Сессия телеграмм аккаунт для автопокупки была завершена! Для возобновления автопокупки войдите в аккаунт снова.</b>'
        )
        loguru.logger.error(f'Telegram session was destroyed. Please reconnect.')
        asyncio.get_running_loop().stop()


async def start_autobuy(
        client: TelegramClient,
        config: AppConfig,
        scheduler: BaseScheduler,
) -> None:
    owner_id = (await client.get_me(input_peer=True)).user_id
    bprovider: BalanceProvider = DefaultBalanceProvider(client=client)
    gprovider: GiftProvider = DefaultGiftProvider(client=client)
    notifier: Notifier = TelegramNotifier(token=config.telegram.bot_token, user_ids=[owner_id])
    scheduler.add_job(
        func=autobuy,
        kwargs=dict(
            bprovider=bprovider,
            gprovider=gprovider,
            config=config,
            notifier=notifier
        ),
        trigger=IntervalTrigger(
            seconds=config.pause.after_get
        )
    )

    try:
        scheduler.start()
    except SchedulerAlreadyRunningError:
        ...
    finally:
        loguru.logger.success('Autobuy was started')
