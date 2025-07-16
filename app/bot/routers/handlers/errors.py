from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram_dialog.api.exceptions import UnknownIntent

router = Router()


@router.error(ExceptionTypeFilter(UnknownIntent))
async def unknown_intent_handler(event: ErrorEvent):
    call = event.update.callback_query
    if call:
        try:
            await call.message.delete()
        except TelegramAPIError:
            await call.answer(
                text='⚠️ Данная кнопка устарела! Воспользуйтесь /start!',
                show_alert=True,
            )
