from tortoise import Tortoise


async def init_db(db_url: str) -> None:
    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["app.database.models"]}
    )
    await Tortoise.generate_schemas()
