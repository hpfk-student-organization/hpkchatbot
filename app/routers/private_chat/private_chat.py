from aiogram import Router

from filters.chat_type import ChatTypeMessageFilter, ChatTypeCallbackFilter
from middlewares.add_new_user import AddNewUserMessageMiddleware

router = Router()

router.message.filter(
    ChatTypeMessageFilter(['private']),

)
router.message.outer_middleware(
    AddNewUserMessageMiddleware()
)


router.callback_query.filter(
    ChatTypeCallbackFilter(chat_type=['private']),
)
