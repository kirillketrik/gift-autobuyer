from aiogram import BaseMiddleware
from aiogram.types import Update
from typing import Callable, Awaitable, Dict, Any, List


class AccessControlOuterMiddleware(BaseMiddleware):
    def __init__(self, allowed_user_ids: List[int]):
        self._allowed_user_ids = allowed_user_ids

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id
        else:
            return None

        if user_id is None or user_id not in self._allowed_user_ids:
            return None

        return await handler(event, data)
