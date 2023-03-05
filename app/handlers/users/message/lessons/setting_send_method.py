from loguru import logger

from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.types import CallbackQuery

from keyboards.default import LessonsKb
from keyboards.inline.inline_keyboard import LessonsIKb, LessonsCBData
from routers.private_chat.private_chat import router
from states import LessonsStates
from utils.mysql import Replacements


@router.message(
    Text(text=LessonsKb.how_get_replacements_btn),
    StateFilter(LessonsStates.menu_settings)
)
async def get_inl_kb_with_setting(message: types.Message):
    """Отримуємо кнопку із налаштуваннями"""
    message_text = 'В цьому пункті ти можеш обрати, яким чином ти плануєш отримувати заміни, або зовсім не отримувати'
    status, send_method = Replacements().get_subscription_status_and_send_method(telegram_id=message.from_user.id)
    await message.answer(
        text=message_text,
        reply_markup=LessonsIKb().setting_send_replacements(
            status=status,
            send_method=send_method
        )
    )


@router.callback_query(
    LessonsCBData.filter(),
    StateFilter(LessonsStates.menu_settings)
)
async def inline_menu_setting_method_replacements(query: CallbackQuery, callback_data: LessonsCBData):
    type_inl_btn: str = callback_data.type_inl_btn
    callback_id: int = callback_data.callback_id
    logger.debug("{}:{}".format(type_inl_btn, callback_id))

    if type_inl_btn == 'status':
        Replacements().update_subscription_status(telegram_id=query.from_user.id, status=callback_id)
    else:
        Replacements().update_subscription_send_method(telegram_id=query.from_user.id, send_method=callback_id)

    status, send_method = Replacements().get_subscription_status_and_send_method(telegram_id=query.from_user.id)

    await query.message.edit_reply_markup(
        reply_markup=LessonsIKb().setting_send_replacements(
            status=status,
            send_method=send_method
        )
    )
    await query.answer(cache_time=0)
