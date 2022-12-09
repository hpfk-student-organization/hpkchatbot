import logging
from abc import ABC
from typing import Union, Optional

from aiogram import types
from aiogram.filters import BaseFilter


async def _check(callback_data: Union[str, list, tuple, set, frozenset], message: types.Message):
    if message.reply_to_message is None:
        logging.debug("Message must be to reply message")
        return False
    elif message.reply_to_message.reply_markup is None:
        logging.debug("Message must be have inline_kb")
        return False
    elif message.reply_to_message.reply_markup.inline_keyboard is None:
        logging.debug("Message must be have inline_kb")
        return False
    elif not isinstance(message.reply_to_message.reply_markup.inline_keyboard, list) and not \
            len(message.reply_to_message.reply_markup.inline_keyboard):
        logging.debug("Message must be have inline_kb")
        return False
    elif not message.reply_to_message.reply_markup.inline_keyboard[0] is None and not \
            len(message.reply_to_message.reply_markup.inline_keyboard):
        logging.debug("Message must be have inline_kb")
        return False
    elif message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data is None:
        logging.debug("Message must be have inline_kb")
        return False

    data = message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split(':')[0]

    if isinstance(callback_data, str):
        return data == callback_data
    return data in callback_data


class __CheckCallbackBaseFilter(BaseFilter, ABC):
    def __init__(self, callback_data: Union[str, list, tuple, set, frozenset]):
        self.callback_data = callback_data


class CheckCallbackMessageFilter(__CheckCallbackBaseFilter):

    async def __call__(self, message: types.Message) -> Optional[bool]:
        return await _check(callback_data=self.callback_data, message=message)
