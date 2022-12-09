from abc import ABC
from typing import Optional, Union, Any

from aiogram import types
from aiogram.filters import BaseFilter


async def _check(group_id: Optional[Any], chat: types.Chat) -> Optional[bool]:
    if isinstance(group_id, int):
        return chat.id == group_id
    return chat.id in group_id


class __GroupIDBaseFilter(BaseFilter, ABC):

    def __init__(self, group_id: Union[int, list, tuple, set, frozenset]):
        self.group_id = int(group_id)


class GroupIDMessageFilter(__GroupIDBaseFilter):
    """Перевірки, чи збігається ID"""

    async def __call__(self, message: types.Message) -> Optional[bool]:
        return await _check(group_id=self.group_id, chat=message.chat)


class GroupIDCallbackFilter(__GroupIDBaseFilter):
    """Перевірки, чи збігається ID"""

    async def __call__(self, query: types.CallbackQuery) -> Optional[bool]:
        return await _check(group_id=self.group_id, chat=query.message.chat)
