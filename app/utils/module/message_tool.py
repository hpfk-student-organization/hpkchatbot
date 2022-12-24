from loguru import logger
import os
from typing import Optional, List

from aiogram import types
from aiogram.types import FSInputFile, InputMediaPhoto, Message, InputFile

import config
from settings import global_storage
from utils.module.redis import RedisGlobalStorage
from utils.tools import get_dir_hash


class ErrorEntryData(Exception):
    def __init__(self, message: Optional[str]):
        self.message = message

class EmptyDir(Exception):
    def __init__(self, message: Optional[str], path: Optional[str]):
        self.message = message
        self.path = path


class ErrorSend(Exception):
    def __init__(self, message: Optional[str]):
        self.message = message


class CashingSendPhotos:
    """Клас, який відповідає, за збереження в кеші фото та отрмання фото з кешу"""

    def __init__(self, message: types.Message, redis: RedisGlobalStorage, key: str):
        if not isinstance(message, types.Message):
            raise ValueError('\'message\' should be types {types}'.format(types=types.Message))

        if not isinstance(key, str):
            raise ValueError('\'redis\' should be types {types}'.format(types=RedisGlobalStorage))

        self.message = message
        self.redis = redis
        self.key = key

    async def get_photo(
            self, dir_path: str,
            upload_photo_text: str = '⏳ Одну хвилинку, шукаю фото...🖼',
            file_no_found_text: str = 'Фото немає',
            fail_send_text: str = 'Не вдалося зібрати всі фото через негідника, котрий їх зберіг'
    ) -> tuple[Message, list[Message] | None]:
        logger.info('Start process send replacements...')
        notification_upload_message = await self.message.answer(
            text=upload_photo_text
        )

        # get hash with dir
        get_hash_dir_for_check_original_files_in_dir = get_dir_hash(path_to_dir=dir_path)

        try:
            list_messages_of_send = await self.__send_replacements_for_user(
                hash_dir=get_hash_dir_for_check_original_files_in_dir, path_to_dir=dir_path)
        except EmptyDir as error:
            logger.debug(error)
            list_messages_of_send = await self.message.answer(file_no_found_text)

        except ErrorSend as error:
            logger.debug(error)
            list_messages_of_send = await self.message.answer(fail_send_text)

        photo_replacements_id = await get_file_id_with_list_photo(list_message=list_messages_of_send)
        logger.info(f'Starting process send replacements - Finish. '
                     f'Send photo message status - {bool(photo_replacements_id)}')
        key = {
            f'photo_replacements_id_{self.key}': photo_replacements_id,
            f'hash_dir_with_photo_replacements_{self.key}': get_hash_dir_for_check_original_files_in_dir
        }
        # save param in redis
        await global_storage.set_data(
            **key
        )
        logger.debug('Saving key in redis for fasted send replacements photo')

        return notification_upload_message, list_messages_of_send

    async def __send_replacements_for_user(self, hash_dir: str, path_to_dir: str) -> Optional[list[types.Message]]:
        key_replacements = f'photo_replacements_id_{self.key}'
        key_last_hash_save = f'hash_dir_with_photo_replacements_{self.key}'

        logger.debug('Getting file_id with redis_store')
        list_file_id = await global_storage.get_data(key_replacements)
        logger.debug(f'Result search: File ID {list_file_id}')

        if list_file_id and hash_dir == await global_storage.get_data(key_last_hash_save):
            logger.debug('file_id and hash dir - status OK. Try send photo, using file_id ')

            # If file_id is exists in memory...
            media_album = await get_media_album_with_list_file_id(list_file_id=list_file_id )
            logger.debug('Create media album use file_id')
            # Try to send message
            try:
                logger.debug('Try send media using file_id')
                return await self.message.answer_media_group(media=media_album)
            except Exception as error:
                logger.warning(f'No send message replacements using file_id method. Error - {error}')

        logger.debug(
            'Try send photo, using file with storage. '
            'Because file_id or hash dir - status Fail or get error when media album is send'
        )
        # If file_id not found, to download files with file storage
        media_album = await get_media_album_with_list_file_storage(path=path_to_dir)
        logger.debug('Create media album use file with storage')
        if not media_album:
            raise EmptyDir('Not found files in file storage', path_to_dir)
        try:
            logger.debug('Try send photo from file storage')

            return await self.message.answer_media_group(media=media_album)
        except Exception as error:
            raise ErrorSend(f'No send message replacements using storage method. Error - {error}')


async def get_media_album_with_list_file_storage(path: Optional[str], caption: Optional[str] = None) -> Optional[list]:
    """
        Download file with file storage

    Returns:

    """
    media_album = list()
    # Get all file in dir with replacements and send later
    list_file = os.listdir(path)
    for file in list_file:
        if len(media_album) >= config.LIMIT_SEND_PHOTO:
            logger.debug('Get replacements photo in media_album with file storage using limit')
            return media_album
        __path = os.path.abspath(os.path.join(path, file))
        media_album.append(
            InputMediaPhoto(
                media=FSInputFile(
                    path=__path,
                ),
                caption=caption
            )
        )
    logger.debug('Get replacements photo in media_album with file storage')
    return media_album


async def get_media_album_with_list_file_id(list_file_id: Optional[list], caption: Optional[str] = None):
    media_album = list()
    for file_id in list_file_id:
        if len(media_album) >= config.LIMIT_SEND_PHOTO:
            logger.debug('Get replacements photo in media_album with file_id using limit')
            return media_album

        if not len(media_album):
            media_album.append(InputMediaPhoto(media=file_id, caption=caption))
            continue

        media_album.append(InputMediaPhoto(media=file_id))
    logger.debug('Get replacements photo in media_album with file_id')
    return media_album


async def get_file_id_with_list_photo(
        list_message: Optional[list]
) -> Optional[List[int | str] | None]:
    """
        Get list with file_id photo send

    Args:
        list_message:

    Returns:

    """
    if not isinstance(list_message, list | tuple):
        return

    if not isinstance(list_message[0], types.Message):
        return

    list_album_file_id = list()
    for message in list_message:
        message: types.Message
        if message.photo is not None:
            list_album_file_id.append(message.photo[-1].file_id)
    return list_album_file_id


async def get_message_id_with_list_photo(
        list_message: Optional[list | types.Message]
) -> Optional[list | int | None]:
    """
        Get message_id list messages or one message

    Args:
        list_message:

    Returns:

    """
    if list_message is None:
        return

    if isinstance(list_message, types.Message):
        return list_message.message_id

    list_message_id = list()
    for message in list_message:
        message: types.Message
        list_message_id.append(message.message_id)
    return list_message_id
