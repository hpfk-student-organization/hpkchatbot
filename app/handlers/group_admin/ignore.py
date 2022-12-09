import logging

from aiogram import types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.group_chat.for_admin import router


@router.message(StateFilter('*'))
async def ignore_in_admin_chat_message(message: types.Message):
    """Ловимо неопрацьований Update в чаті admin"""
    return
    # await message.answer(_cTtM('Unknown message in admin chat!'))


@router.callback_query(StateFilter('*'))
async def ignore_in_admin_chat_callback(query: CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup()
    await query.answer('Не розумію')
    logging.debug('Ignore clicking in admin group')
