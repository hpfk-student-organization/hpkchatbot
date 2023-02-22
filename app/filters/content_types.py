from abc import ABC
from typing import Union, Optional

from aiogram import enums, types
from aiogram.filters import BaseFilter


class __ContentTypesBaseFilter(BaseFilter, ABC):
    def __init__(self, content_types: Union[enums.ContentType, list, tuple, set, frozenset]):
        self.content_types = content_types


class ContentTypesFilter(__ContentTypesBaseFilter):
    """Перевірки, чи збігається тип"""

    async def __call__(self, message: types.Message) -> Optional[bool]:
        return message.content_type == self.content_types or message.content_type in self.content_types
