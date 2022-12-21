from loguru import logger

from aiogram import types

from routers.excention import router


@router.errors()
async def another_exceptions(update: types.Update, file_exception, exception):
    """Unknown error in code"""

    logger.error(file_exception)
    logger.error(exception)

