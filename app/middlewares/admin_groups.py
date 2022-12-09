# Даний middleware потрібен, щоб пропустити адмінів. А ті, хто не адміни - сказати, що тикати нельзя.
import logging
from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram import types

from utils.mysql import Users


def _is_admin(user_id: Optional[int]) -> Optional[bool]:
    set_user_id = map(int, Users().get_id_all_admin_in_set())
    if user_id in set_user_id:
        return True
    return False


class CheckAdminMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        logging.debug("Send message in admin group")
        # check for action for only admin in admin group
        if _is_admin(user_id=event.from_user.id):
            logging.debug("Send message in admin group by admin")
            return await handler(event, data)

        # remove message if user not admin
        logging.debug("Send message in admin group not by admin")
        await event.delete()
        logging.debug("Message delete")
        return


# inner-middleware - callback
class CheckAdminCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: types.CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        logging.debug("Click btn on inline_kb in admin group")
        if _is_admin(user_id=event.from_user.id):
            return await handler(event, data)

        await event.answer(
            "Ти не маєш достатніх прав на здійснення даної операції",
            show_alert=True
        )
        return
