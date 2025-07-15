import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from dishka import make_async_container
from loguru import logger

from app.autobuyer import Autobuyer
from app.bot import start_bot
from app.database import init_db
from app.di.container import AppProvider
from app.settings import load_config
from app.utils.telethon import auth


async def main():
    logger.info("Loading configuration...")
    config = load_config()

    logger.info("Starting Telegram client...")
    client = await auth(
        api_id=config.telegram.api_id,
        api_hash=config.telegram.api_hash,
        session=config.telegram.session
    )
    user = await client.get_me(input_peer=False)
    config.telegram.admin_id = user.id
    logger.success(f"Telegram client authenticated as @{user.username} (ID: {user.id})")

    logger.info("Initializing database...")
    await init_db(db_url=config.db_url)
    logger.success("Database initialized successfully.")

    logger.info("Creating dependency container...")
    provider = AppProvider(client=client, config=config)
    container = make_async_container(provider)

    async with container(lock_factory=asyncio.Lock) as nested_container:
        logger.info("Retrieving Autobuyer instance from DI container...")
        autobuyer = await nested_container.get(Autobuyer)

        logger.info(f"Scheduling autobuy job every {config.pause.after_get} seconds...")
        scheduler = AsyncIOScheduler()
        scheduler.add_job(
            func=autobuyer.autobuy,
            trigger=IntervalTrigger(seconds=config.pause.after_get),
        )
        scheduler.start()
        logger.success("Autobuyer job scheduled and scheduler started.")

        logger.info("Starting bot...")
        await start_bot(
            bot_token=config.telegram.bot_token,
            admin_ids=[config.telegram.admin_id],
            container=nested_container
        )


if __name__ == '__main__':
    try:
        logger.info("Launching main application...")
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError) as e:
        logger.warning(f"Application interrupted: {e}")
        exit(-1)
