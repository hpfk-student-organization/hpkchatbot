import inspect
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from loguru import logger

import config


def to_correct_format_error_trace(error_list: list):
    error: inspect.FrameInfo
    text_error=''
    for error in error_list[::-1]:
        if '\{}\\'.format(config.VENV_DIR_NAME) in error.filename:  # if file in found in venv
            continue
        filename = error.filename
        name_func = error.function
        line = error.lineno
        values_in_func = error.frame.f_locals
        text_error += '\n\tfilename: "{0}"\n\tfunction: "{1}" - line: {2}\n\tvalues: {3}\n'.format(
            filename, name_func, line, values_in_func
        )
    return text_error


class GetNameFunctionMiddleware(BaseMiddleware):
    """

    Даний Middleware дозволяє отримати інформацію про файл, в якому виникла помилка

    """


    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],

    ) -> Any:
        info_file_exception = inspect.trace()  # get information about function calls

        data.update(
            {'file_exception': to_correct_format_error_trace(info_file_exception),
             'exception': event.dict().get(
                 'exception', None)
             })  # add in dict new param with info about error file
        return await handler(event, data)
