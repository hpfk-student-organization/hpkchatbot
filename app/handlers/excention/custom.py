from aiogram.filters import ExceptionTypeFilter
from aiogram.types.error_event import ErrorEvent

from routers.excention import router
from utils.module.message_tool import ErrorEntryData


@router.errors(ExceptionTypeFilter(ErrorEntryData))
async def entry_date_exceptions(error_event: ErrorEvent):
    """Unknown error in code"""

    text = error_event.exception

    callback_query = error_event.update.callback_query

    await callback_query.answer(str(text))
