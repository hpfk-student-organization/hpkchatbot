from aiogram import types
from aiogram.filters import StateFilter, Text

import config
from keyboards.default import LessonsKb
from routers.private_chat.private_chat import router
from settings import global_storage
from states import LessonsStates
from utils.module.message_tool import CashingSendPhotos


@router.message(
    Text(text=LessonsKb.hours_lessons_btn),
    StateFilter(LessonsStates.main_menu)
)
async def get_photo_with_time_book(message: types.Message):
    """Отримуємо фото занять, які в нас присутні"""
    caching = CashingSendPhotos(message=message, redis=global_storage, key='time_book')
    notification_upload_message, _ = await caching.get_photo(
        dir_path=config.PATH_TO_PHOTO_TIME_BOOK
    )

    await notification_upload_message.delete()
