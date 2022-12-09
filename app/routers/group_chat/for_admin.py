from aiogram import Router

import config
from filters.chat_type import ChatTypeMessageFilter, ChatTypeCallbackFilter
from filters.check_id_group import GroupIDCallbackFilter, GroupIDMessageFilter
from middlewares.admin_groups import CheckAdminMessageMiddleware, CheckAdminCallbackMiddleware

router = Router()

router.message.filter(
    ~ChatTypeMessageFilter(['private']),
    GroupIDMessageFilter(config.ID_GROUP_ADMIN)

)
router.message.middleware(
    CheckAdminMessageMiddleware()
)

router.callback_query.filter(
    ~ChatTypeCallbackFilter(['private']),
    GroupIDCallbackFilter(config.ID_GROUP_ADMIN)
)
router.callback_query.middleware(
    CheckAdminCallbackMiddleware()
)
