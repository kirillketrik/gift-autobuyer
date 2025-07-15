from aiogram import Router

from . import create_filters, delete_filters, set_receivers, main_menu

router = Router()
router.include_routers(
    create_filters.dialog,
    delete_filters.delete_filters_dialog,
    set_receivers.set_receivers_dialog,
    main_menu.main_menu_dialog,
)
