from loguru import logger

import aiogram
from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType

from filters.content_types import ContentTypesFilter
from keyboards.default import AnonymousChatKb
from routers.private_chat.private_chat import router
from states import AnonymousChatStates
from utils.module.state import FSMContextCustoms
from utils.mysql import AnonimChat


async def send_message_and_kb(message: types.Message, text, reply_markup):
    await message.answer(
        text=text, reply_markup=reply_markup
    )


@router.message(Text(text=AnonymousChatKb.leave_chat_btn), StateFilter(AnonymousChatStates.chat_message))
async def leave_with_anonim_chat(message: types.Message):
    """Якщо хто із користувачів вирішив покинути чат"""
    message_text = "Ти точно хочеш завершити чат? Співрозмовника буде втрачено."
    await send_message_and_kb(message=message, text=message_text, reply_markup=AnonymousChatKb.exit_chat())


@router.message(Text(text=AnonymousChatKb.back_in_chat_btn), StateFilter(AnonymousChatStates.chat_message))
async def continue_talk_with_user(message: types.Message):
    """Якщо ти передумав покидати чат"""
    message_text = "Ти продовжив листування з співрозмовником"
    await send_message_and_kb(message=message, text=message_text, reply_markup=AnonymousChatKb.kb_in_chat())


@router.message(Text(text=AnonymousChatKb.hide_keyboard_btn), StateFilter(AnonymousChatStates.chat_message))
async def hide_kb_in_chat(message: types.Message):
    """Якщо ти ховаєш клавіатуру"""
    message_text = "Клавіатура схована. Щоб повернути клавіатуру - надішли команду " \
                   "/show_keyboard"
    await send_message_and_kb(message=message, text=message_text, reply_markup=types.ReplyKeyboardRemove())


@router.message(Text(text=AnonymousChatKb.exit_chat_btn), StateFilter(AnonymousChatStates.chat_message))
async def exit_with_chat(message: types.Message, state: FSMContext, bot: aiogram.Bot):
    """Якщо хто із користувачів все ж таки вирішив покинути остаточно чат"""
    message_text = "Листування завершено!"
    message_text_for_another_user = "Співрозмовник завершив листування!"
    reply_markup = AnonymousChatKb.search_or_exit_in_menu()
    connect_with = AnonimChat().get_telegram_id_with_connect(telegram_id=message.from_user.id)
    await send_message_and_kb(message=message, text=message_text, reply_markup=reply_markup)
    await bot.send_message(
        chat_id=connect_with,
        text=message_text_for_another_user,
        reply_markup=reply_markup
    )

    AnonimChat().update_connect_with(telegram_id=message.from_user.id, connect_with_telegram_id=None)
    AnonimChat().update_connect_with(telegram_id=connect_with, connect_with_telegram_id=None)
    for telegram_id in (message.from_user.id, connect_with):
        state_new = FSMContextCustoms(state=state, user_id=telegram_id, chat_id=telegram_id)
        await state_new.set_state(AnonymousChatStates.close_chat)


async def get_raise_if_two_user_not_connect(telegram_id):
    if AnonimChat().get_telegram_id_with_connect(telegram_id=telegram_id) is None:
        raise Exception(
            "During communication in the anonymous chat, an error occurred by one of the users - "
            "there is no pair, one of the two interlocutors"
        )


@router.message(ContentTypesFilter(
    [ContentType.TEXT, ContentType.PHOTO, ContentType.ANIMATION, ContentType.DOCUMENT, ContentType.STICKER,
     ContentType.VOICE, ContentType.VIDEO_NOTE, ContentType.LOCATION, ContentType.POLL, ContentType.AUDIO,
     ContentType.CONTACT, ContentType.VIDEO]),
    StateFilter(AnonymousChatStates.chat_message)
)
async def processing_in_chat_with_message(message: types.Message, bot: aiogram.Bot):
    """Обробка спілкування"""
    connect_with = AnonimChat().get_telegram_id_with_connect(telegram_id=message.from_user.id)
    await get_raise_if_two_user_not_connect(connect_with)

    await message.copy_to(
        chat_id=connect_with,
    )
    AnonimChat().add_one_message_to_all_message(telegram_id=message.from_user.id)


@router.message(StateFilter(AnonymousChatStates.chat_message))
async def processing_in_chat_with_message(message: types.Message, bot: aiogram.Bot):
    """Якщо користувач надіслав об'єкт, якого немає в обробці"""
    logger.warning("No support this content_type - {0}".format(message.content_type))


@router.edited_message(StateFilter(AnonymousChatStates.chat_message))
async def processing_edit_text_in_chat_with_message(message: types.Message, bot: aiogram.Bot):
    """Якщо користувач змінив об'єкт, якого немає в обробці"""
    logger.warning("No support edit text")
    return

