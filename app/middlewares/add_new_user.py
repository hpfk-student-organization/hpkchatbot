from loguru import logger
from datetime import datetime
from typing import Callable, Dict, Any, Awaitable, Optional

from aiogram import BaseMiddleware
from aiogram import types

# Inner-мидлварь на добавлення користувачів в нову БД


# middleware - message send
from utils.mysql import Replacements, Users


class AddNewUserMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        await update_information_about_user_in_databases(
            telegram_id=event.from_user.id,
            username=event.from_user.username
        )
        logger.debug("Add or update info for user in databases")
        return await handler(event, data)


async def update_information_about_user_in_databases(
        telegram_id: Optional[int | str],
        username: Optional[str]
):
    user_old_actions = user_register = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    if not Users().is_check_exist_user(telegram_id=telegram_id):
        Users().add_new_user(
            telegram_id=telegram_id,
            user_old_actions=user_old_actions,
            user_register=user_register,
            username=username
        )
    else:
        Users().update_info_user(
            telegram_id=telegram_id,
            user_old_actions=user_old_actions,
            username=username
        )
    if not Replacements().is_check_exist_user(telegram_id=telegram_id):
        # Add user in databases for replacements
        Replacements().add_new_user_for_replacements(
            telegram_id=telegram_id
        )
