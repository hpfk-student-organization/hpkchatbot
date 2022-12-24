from aiogram.types.error_event import ErrorEvent
from loguru import logger

from routers.excention import router


@router.errors()
async def another_exceptions(error_event: ErrorEvent, file_exception, exception):
    """Unknown error in code"""

    logger.error(file_exception)
    logger.error(error_event.exception)
