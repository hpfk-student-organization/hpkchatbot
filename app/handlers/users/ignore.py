from aiogram import types, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from routers.private_chat.private_chat import router


# @router.message(lambda message: message.chat.type == 'private', StateFilter(state='*'))
@router.message(F.text.startswith('/'), StateFilter('*'))
async def ignore_command_private_message(message: types.Message):
    message_test = 'Тут дана команда не працює. '
    await message.answer(text=message_test)


@router.message(StateFilter('*'))
async def ignore_private_message(message: types.Message, state: FSMContext):
    """Ловимо неопрацьований Update"""
    message_text = 'Я тебе не розумію. 😕'
    await message.answer(
        text=message_text
    )


@router.callback_query(StateFilter('*'))
async def ignore_private_message(query: CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup()
    await query.answer('Тут це не працює')
