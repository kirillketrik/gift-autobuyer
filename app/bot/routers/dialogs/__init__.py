from aiogram import Router

from . import create_filters, delete_filters, filters_menu, main_menu, receiver_menu, set_receivers

router = Router()
router.include_routers(
    create_filters.dialog,
    delete_filters.delete_filters_dialog,
    filters_menu.filter_dialog,
    main_menu.main_menu_dialog,
    receiver_menu.receivers_dialog,
    set_receivers.set_receivers_dialog,
)
