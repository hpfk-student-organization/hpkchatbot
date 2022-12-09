import asyncio
from typing import Optional

from aiogram import types


class Animations:

    def __init__(self, message: types.Message, message_text: Optional[str]):
        self.message: types.Message = message
        self.message_text: str = message_text

    async def printing(self, time: Optional[float] = 0.05):
        message_text = self.message_text

        done_text = ''
        typing_symbol = '▒'
        while message_text:
            await self.message.edit_text(text=done_text + typing_symbol)
            await asyncio.sleep(time)
            done_text = done_text + message_text[0]  # приписуємо +1 символ
            message_text = message_text[1:]  # видаляємо 1 символ
            await self.message.edit_text(text=done_text)
            await asyncio.sleep(time)

    async def replace_emoji(self, time: Optional[float] = 3.1):
        message_text = self.message_text

        await asyncio.sleep(time + 0.39)
        for emoji in message_text.split():
            if not self.message.text == emoji:
                await self.message.edit_text(
                    text=emoji
                )
                await asyncio.sleep(time)


async def get_animation(message: types.Message, message_text: str):
    match message_text:
        case 'З днем ПI_шника!':
            _message = await message.answer(message_text[0])
            return asyncio.create_task(Animations(message=_message, message_text=message_text).printing())
        case 'З днем дурня!':
            await message.answer(message_text)
            _message = await message.answer('😈')
            return asyncio.create_task(Animations(message=_message, message_text='😇').replace_emoji())
        case 'Happy Halloween!🎃':
            await message.answer(message_text)
            await message.answer("🎃")
            return None
