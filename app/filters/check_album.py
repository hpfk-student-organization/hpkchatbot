from typing import Union, Optional

from aiogram import types
from aiogram.filters import BaseFilter


class CheckAlbumMessageFilter(BaseFilter):

    async def __call__(self, message: types.Message) -> Optional[bool]:
        return bool(message.media_group_id)
