from aiogram.fsm.state import StatesGroup, State


class AuthSG(StatesGroup):
    phone = State()
    code = State()
    password = State()


class MainMenuSG(StatesGroup):
    menu = State()


class EditGiftFilterSG(StatesGroup):
    select_mode = State()
    input_promt = State()
    input_manually = State()
    confirm = State()


class DeleteFilterSG(StatesGroup):
    input_ids = State()
    confirm = State()


class SetReceiversSG(StatesGroup):
    input_usernames = State()
    confirm = State()
