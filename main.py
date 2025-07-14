import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import TelegramClient
from telethon.sessions import StringSession

from app.autobuyer import start_autobuy, auth
from app.bot import start_bot
from app.database import init_db
from app.settings import load_config


async def main():
    config = load_config()
    scheduler = AsyncIOScheduler()

    client = await auth(
        api_id=config.telegram.api_id,
        api_hash=config.telegram.api_hash,
    )

    user = await client.get_me(input_peer=True)

    await init_db(db_url=config.db_url)
    await start_autobuy(
        client=client,
        config=config,
        scheduler=scheduler,
    )
    await start_bot(
        bot_token=config.telegram.bot_token,
        admin_ids=[user.user_id],
        context={
            'config': config
        }
    )


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        exit(-1)
