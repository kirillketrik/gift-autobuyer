from aiogram import Router, types
from aiogram.filters import Command
from aiogram_dialog import DialogManager, StartMode, ShowMode

from app.bot.states import MainMenuSG

router = Router()


@router.message(Command('start'))
async def start_bot(_msg: types.Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=MainMenuSG.menu,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.DELETE_AND_SEND
    )
