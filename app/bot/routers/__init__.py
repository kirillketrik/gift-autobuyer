from aiogram import Router

from . import dialogs, handlers

router = Router()
router.include_routers(
    handlers.router,
    dialogs.router,
)
