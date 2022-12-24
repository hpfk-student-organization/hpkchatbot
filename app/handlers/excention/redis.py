import aiogram
from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent
from loguru import logger
from redis import exceptions

from routers.excention import router


@router.errors(ExceptionTypeFilter(exceptions.ConnectionError))
async def redis_exceptions_connection(error_event: ErrorEvent, file_exception, exception):
    logger.error(file_exception)
    logger.error(error_event.exception)
    message_text = 'Сталася помилка. С пробуй пізніше'
    message = error_event.update.message
    if message is not None:
        await message.answer(text=message_text)
