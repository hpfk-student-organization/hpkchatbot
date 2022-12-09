from abc import ABC
from typing import Union

from aiogram import types
from aiogram.filters import BaseFilter


class __EventTypeBaseFilter(BaseFilter, ABC):
    def __init__(self, *event_type: Union[str, list, tuple, set, frozenset]):
        self.event_type = event_type


class EventTypeFilter(__EventTypeBaseFilter):

    async def __call__(self, update: types.Update) -> bool:
        return update.event_type == self.event_type or update.event_type in self.event_type
