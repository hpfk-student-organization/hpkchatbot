from abc import ABC
from typing import Union, Optional

from aiogram import types
from aiogram.filters import BaseFilter


async def _check(chat_type: Union[str, list, tuple, set, frozenset], chat: types.Chat):
    if isinstance(chat_type, str):
        return chat.type == chat_type
    return chat.type in chat_type


class __ChatTypeBaseFilter(BaseFilter, ABC):
    def __init__(self, chat_type: Union[str, list, tuple, set, frozenset]):
        self.chat_type = chat_type


class ChatTypeMessageFilter(__ChatTypeBaseFilter):
    async def __call__(self, message: types.Message) -> Optional[bool]:
        return await _check(chat_type=self.chat_type, chat=message.chat)


class ChatTypeCallbackFilter(__ChatTypeBaseFilter):

    async def __call__(self, query: types.CallbackQuery) -> Optional[bool]:
        return await _check(chat_type=self.chat_type, chat=query.message.chat)
