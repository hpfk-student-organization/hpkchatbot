import logging
from typing import List, Optional

import aiogram
from aiogram import types, F
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType
from aiogram_media_group import media_group_handler

import config
from filters.check_album import CheckAlbumMessageFilter
from filters.content_types import ContentTypesFilter
from keyboards.default import LessonsKb
from keyboards.inline.inline_keyboard import VerificationReplacementsIKb
from routers.private_chat.private_chat import router
from states import LessonsStates
from utils.module.message_tool import get_file_id_with_list_photo, get_media_album_with_list_file_id
from utils.mysql import MediaFileID


@router.message(
    Text(text=LessonsKb.send_new_replacements_btn),
    StateFilter(LessonsStates.main_menu)
)
async def send_new_photo_for_replacements(message: types.Message, state: FSMContext, bot: aiogram.Bot):
    """Go to menu with send photo replacements with main menu lesson"""

    message_text = 'Надішліть мені фото сьогоднішніх замін, а я їх викладу в замінах'
    await message.answer(
        text=message_text,
        reply_markup=LessonsKb.back()
    )
    logging.debug("Remove file_id with databases")
    MediaFileID().delete(telegram_id=message.from_user.id, type_file_id='replacement')
    await state.set_state(LessonsStates.send_new_replacements)


@router.message(
    CheckAlbumMessageFilter(),
    ContentTypesFilter(ContentType.PHOTO),
    StateFilter(LessonsStates.send_new_replacements)
)
@media_group_handler
async def get_media_album_zip_photo_replacements(messages: List[types.Message], bot: aiogram.Bot):
    """
    Get media photo album in message
    """
    saving_album_message_text = "⏳ Зберігаю фото в фотокарточку..."
    save_album_message_text = 'Альбом збережений'

    # path = os.path.join(config.PATH_TO_PHOTO_REPLACEMENTS_TMP, str(message.from_user.id))

    await get_media_album(
        message=messages[0],
        saving_message_text=saving_album_message_text,
        save_message_text=save_album_message_text,
        list_file_id=await get_file_id_with_list_photo(list_message=messages)
    )


async def get_media_album(
        message: types.message,
        saving_message_text: Optional[str],
        save_message_text: Optional[str],
        list_file_id: Optional[List[str] | str]
):
    """
    Global function for procedures saving photo replacements

    """
    type_file_id = 'replacement'

    photo_album_download_notification_message = await message.answer(
        text=saving_message_text
    )
    logging.debug('Get file_id')
    await save_file_id_in_database(
        list_file_id=list_file_id,
        telegram_id=message.from_user.id,
        type_file_id=type_file_id
    )
    await photo_album_download_notification_message.delete()
    await message.reply(text=save_message_text)
    await get_and_send_album_with_databases(message=message, type_file_id=type_file_id)


async def save_file_id_in_database(
        list_file_id: Optional[List[str] | str], telegram_id: Optional[int | str], type_file_id: Optional[str]
):
    """
    Function for saving file_id with telegram in databases
    """
    logging.debug("Saving list file_id in databases")

    if isinstance(list_file_id, str):
        list_file_id = [list_file_id]

    for file_id in list_file_id:
        if len(MediaFileID().get(telegram_id=telegram_id)) >= config.LIMIT_SEND_PHOTO:
            return
        MediaFileID().add(telegram_id=telegram_id, file_id=file_id, type_file_id=type_file_id)


async def get_and_send_album_with_databases(message: types.message, type_file_id: Optional[str]):
    message_text_information = 'Виберіть наступні ваші дії:\n' \
                               'Відправити заміни на перевірку анонімно\n' \
                               'Відправити заміни на перевірку залишивши посилання на себе\n\n' \
                               'Якщо заміни будуть відправлені з посиланням на себе, то після перевірки, ' \
                               'в розділі Заміни буде посилання на користувача, ' \
                               'якщо таке додане в налаштуваннях користувача.\n\n' \
                               'Також, ви можете відправити додаткове фото, до загально списку.'

    media_album = await get_media_album_with_list_file_id(
        list_file_id=MediaFileID().get(telegram_id=message.from_user.id, type_file_id=type_file_id)
    )
    await message.answer_media_group(media=media_album)
    await message.answer(
        text=message_text_information,
        reply_markup=LessonsKb.send_replacements()
    )


@router.message(
    ContentTypesFilter(ContentType.PHOTO),
    StateFilter(LessonsStates.send_new_replacements)
)
async def get_photo_replacements(message: types.Message):
    """
    Get only 1 photo (not album) replacements
    """

    save_photo_message_text = 'Фото збережено'
    saving_album_message_text = "⏳ Зберігаю фото в фотокарточку..."

    await get_media_album(
        message=message,
        saving_message_text=saving_album_message_text,
        save_message_text=save_photo_message_text,
        list_file_id=message.photo[-1].file_id
    )


@router.message(
    F.document[F.mime_type.contains('image/')],
    ContentTypesFilter(ContentType.DOCUMENT),
    StateFilter(LessonsStates.send_new_replacements)
)
async def get_photo_in_file_replacements(message: types.Message):
    """
    Photo processing without compression
    """

    not_support_photo_in_file_message_text = "Не вдається зберегти. Спробуй відправити фото з стисненням"
    logging.warning("Send user for photo replacements in format - {0}".format(message.document.mime_type))
    await message.answer(text=not_support_photo_in_file_message_text)


@router.message(
    ContentTypesFilter(ContentType.DOCUMENT),
    StateFilter(LessonsStates.send_new_replacements)
)
async def not_support_file(message: types.Message):
    """
    All other documents
    """

    not_support_message_text = "Тип файла не підтримується. Спробуй відправити фото іншого розширення"
    logging.warning("Not found support send user for photo replacements. File - {0}".format(message.document.mime_type))
    await message.answer(text=not_support_message_text)


@router.message(
    ~ContentTypesFilter(ContentType.TEXT) and ContentTypesFilter(ContentType.ANY),
    StateFilter(LessonsStates.send_new_replacements)
)
async def not_support_message(message: types.Message):
    """
    All other content
    """
    not_support_message_text = "Тип повідомлення не підтримується."
    await message.answer(text=not_support_message_text)


@router.message(
    Text(text=(LessonsKb.send_anonim_replacements_btn, LessonsKb.send_replacements_with_username_btn)),
    StateFilter(LessonsStates.send_new_replacements)
)
async def send_replacements_using_anonim_style(message: types.Message, state: FSMContext, bot: aiogram.Bot):
    """
    Send replacements for verif by anonim mode
    """
    type_file_id = 'replacement'
    if not MediaFileID().exist(telegram_id=message.from_user.id, type_file_id=type_file_id):
        # if type is not exist in databases
        message_text = "Фото не знайдено. Потрібно для початку відправити фото"
        await message.answer(
            text=message_text
        )
        return 

    media_album = await get_media_album_with_list_file_id(
        list_file_id=MediaFileID().get(telegram_id=message.from_user.id, type_file_id=type_file_id)
    )
    media_album_message = await bot.send_media_group(
        chat_id=config.ID_GROUP_ADMIN,
        media=media_album,
    )

    show_information_user = False
    if message.text == LessonsKb.send_replacements_with_username_btn:
        show_information_user = True

    message_text = "Заміни станом на {0}"
    message_with_inline_kb = await bot.send_message(
        chat_id=config.ID_GROUP_ADMIN,
        text=message_text.format(message.date.utcnow().strftime("%Y-%m-%d %H:%M")),
        reply_to_message_id=media_album_message[0].message_id,
        reply_markup=VerificationReplacementsIKb().verification(
            user_id=message.from_user.id, show_information_user=show_information_user,
            message_id_send_btn=message.message_id
        )
    )
    # save in database information for send_photo
    MediaFileID().add_file_id_in_replacements_from_tmp_file_id(
        message_id=message_with_inline_kb.message_id,
        telegram_id=message.from_user.id,
        type_file_id=type_file_id
    )

    message_text_reply = 'Заміни передані на перевірку. Дякую'
    await message.reply(
        text=message_text_reply
    )

    from handlers.users.message.back import back_to_lesson_main_menu_with_remove_tmp_file
    await back_to_lesson_main_menu_with_remove_tmp_file(message=message, state=state)
