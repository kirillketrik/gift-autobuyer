from dishka import Provider, Scope, provide
from telethon import TelegramClient

from app.autobuyer import Autobuyer
from app.autobuyer.balance_provider import TelethonBalanceProvider
from app.autobuyer.gift_allocator import DefaultGiftAllocator
from app.autobuyer.gift_provider import TelethonGiftProvider
from app.autobuyer.notifier import TelegramNotifier
from app.core.interfaces.autobuyer import BalanceProvider, GiftProvider, GiftAllocator, Notifier
from app.core.interfaces.repository import GiftFilterRepository, ReceiverRepository
from app.database.repositories import TortoiseGiftFilterRepository, TortoiseReceiverRepository
from app.settings import AppConfig


class AppProvider(Provider):
    def __init__(self, client: TelegramClient, config: AppConfig):
        super().__init__(scope=Scope.APP)
        self.client = client
        self.config = config

    @provide(scope=Scope.APP)
    def provide_config(self) -> AppConfig:
        return self.config

    @provide(scope=Scope.APP)
    def provide_balance_provider(self) -> BalanceProvider:
        return TelethonBalanceProvider(client=self.client)

    @provide(scope=Scope.APP)
    def provide_gift_provider(self) -> GiftProvider:
        return TelethonGiftProvider(client=self.client)

    @provide(scope=Scope.APP)
    def provide_gift_allocator(self) -> GiftAllocator:
        return DefaultGiftAllocator()

    @provide(scope=Scope.APP)
    def provide_gift_filter_repository(self) -> GiftFilterRepository:
        return TortoiseGiftFilterRepository()

    @provide(scope=Scope.APP)
    def provide_receiver_repository(self) -> ReceiverRepository:
        return TortoiseReceiverRepository()

    @provide(scope=Scope.APP)
    def provide_notifier(self) -> Notifier:
        return TelegramNotifier(
            token=self.config.telegram.bot_token,
            user_ids=[self.config.telegram.admin_id]
        )

    @provide(scope=Scope.APP)
    def provide_autobuyer(self) -> Autobuyer:
        autobuyer = Autobuyer(
            gift_filter_reader=self.provide_gift_filter_repository(),
            gift_allocator=self.provide_gift_allocator(),
            gift_provider=self.provide_gift_provider(),
            receiver_reader=self.provide_receiver_repository(),
            balance_provider=self.provide_balance_provider(),
            notifier=self.provide_notifier(),
            pause_after_buy=self.config.pause.after_buy
        )
        return autobuyer
