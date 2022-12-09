import logging

from aiogram import types

from routers.excention import router


@router.errors()
async def another_exceptions(update: types.Update, file_exception, exception):
    """Unknown error in code"""
    logging.error(file_exception)
    logging.error(exception)

