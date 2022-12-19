from loguru import logger

import aiogram
from aiogram import types, exceptions
from aiogram.filters import ExceptionTypeFilter, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards.default import AnonymousChatKb
from routers.excention import router
from states import LessonsStates, AnonymousChatStates, ForStudentsStates


@router.errors(
    # EventTypeFilter('callback_query'),
    ExceptionTypeFilter(exceptions.TelegramRetryAfter)

)
async def aiogram_exceptions_often_retry_edit_message(update, file_exception):
    """
        Very frequent editing of the message with click to btn

    Args:
        update:

    Returns:

    """

    message_text = 'Охолонь. 🥵 Не варто так часто'
    await update.update.callback_query.answer(text=message_text)


@router.errors(
    # EventTypeFilter('callback_query'),
    ExceptionTypeFilter(exceptions.TelegramBadRequest),
    StateFilter(LessonsStates.menu_settings,ForStudentsStates.main_menu)
)
async def aiogram_exceptions_message_is_not_modified(update, exception, file_exception):
    """IF user clicking inline button two times and telegram not can edit text"""
    await update.update.callback_query.answer(cache_time=0)
    logger.warning(file_exception)
    logger.warning(exception)


@router.errors(
    ExceptionTypeFilter(exceptions.TelegramBadRequest)
)
async def aiogram_exceptions_message_is_not_modified(update, exception, file_exception):
    """
        message is not modified

    Args:
        error:

    Returns:

    """
    await update.update.callback_query.answer(cache_time=0)
    logger.warning(file_exception)
    logger.warning(exception)


@router.errors(
    # EventTypeFilter('callback_query'),
    ExceptionTypeFilter(exceptions.TelegramForbiddenError)

)
async def aiogram_exceptions_user_block_bot(update):
    """
        When user block to bot

    Args:
        update:

    Returns:

    """

    message_text = 'Дія недоступна, так як користувач заблокував бота'
    await update.update.callback_query.answer(text=message_text)


async def send_message_with_kb(bot, state, text):
    await bot.send_message(
        chat_id=state.key.chat_id,
        text=text,
        reply_markup=AnonymousChatKb.search_or_exit_in_menu()
    )
    await state.set_state(AnonymousChatStates.close_chat)


@router.errors(
    StateFilter(AnonymousChatStates.chat_message),
    ExceptionTypeFilter(exceptions.TelegramForbiddenError)
)
async def aiogram_exceptions_telegram_forbidden_in_anonim_chat(
        update, bot: aiogram.Bot, state: FSMContext, file_exception, exception
):
    """
        When user block to bot in anonim_chat

    Args:
        update:

    Returns:
    @param state:
    @param bot:

    """
    logger.warning(file_exception)
    logger.warning(exception)
    message_text = "Співрозмовник завершив листування!"
    await send_message_with_kb(bot=bot, state=state, text=message_text)


@router.errors(
    StateFilter(AnonymousChatStates.chat_message)
)
async def aiogram_exceptions_in_anonim_chat(
        update: types.Update, bot: aiogram.Bot, state: FSMContext, file_exception, exception
):
    """
        When aiogram fish unknown error in anonim_chat

    Args:
        update:

    Returns:
    @param state:
    @param bot:

    """
    logger.warning(file_exception)
    logger.warning(exception)
    message_text = "Сталася невідома помилка під час спілкування із користувачем"

    await send_message_with_kb(bot=bot, state=state, text=message_text)
