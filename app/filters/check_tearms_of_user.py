from abc import ABC
from typing import Union, Optional

from aiogram import types
from aiogram.filters import BaseFilter

from utils.mysql import Users


async def _check(user_id: Optional[int]):
    return Users().check_status_terms_of_user(telegram_id=user_id)


class __CheckTermsOfUserBaseFilter(BaseFilter, ABC):
    def __init__(self, status: Union[bool]):
        self.status = status


class CheckTermsOfUserMessageFilter(__CheckTermsOfUserBaseFilter):
    async def __call__(self, message: types.Message) -> Optional[bool]:
        return await _check(user_id=message.from_user.id) == self.status


class CheckTermsOfUserCallbackFilter(__CheckTermsOfUserBaseFilter):

    async def __call__(self, query: types.CallbackQuery) -> Optional[bool]:
        return await _check(user_id=query.from_user.id) == self.status
