import logging

from aiogram import types
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery

from routers.group_chat.another import router


@router.message(
    StateFilter('*')
)
async def ignore_in_chat_message(message: types.Message):
    """Get unknown message in chat"""
    pass


@router.callback_query(
    StateFilter('*')
)
async def ignore_in_chat_callback(query: CallbackQuery):
    """Get unknown callback in chat"""
    logging.debug("Get unknown callback in chat")
    pass
