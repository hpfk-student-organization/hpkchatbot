from aiogram import types

from routers.group_chat.another import router


@router.message()
async def welcome_group(message: types.Message):
    return
    # await message.reply(_cTtM("Hello Chat!"))
