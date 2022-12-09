import logging

import aiogram
from aiogram import types
from aiogram.filters import ExceptionTypeFilter
from redis import exceptions

from routers.excention import router


@router.errors(ExceptionTypeFilter(exceptions.ConnectionError))
async def redis_exceptions_connection(update: types.Update, file_exception, exception, bot: aiogram.Bot):
    logging.error(file_exception)
    logging.error(exception)
    message_text = 'Сталася помилка. С пробуй пізніше'
    await bot.send_message(text=message_text, chat_id=update.message.chat.id)
