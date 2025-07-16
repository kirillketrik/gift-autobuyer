from aiogram import Router

from . import (
    commands,
    errors,
)

router = Router()
router.include_routers(
    errors.router,
    commands.router,
)
