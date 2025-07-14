from aiogram import Router

from . import commands

router = Router()
router.include_routers(
    commands.router,
)
