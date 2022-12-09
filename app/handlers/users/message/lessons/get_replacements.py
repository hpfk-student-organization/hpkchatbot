import logging
from typing import Optional

import aiogram
from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.types import CallbackQuery

import config
from decorator.cache import cache
from keyboards.default import LessonsKb, MainMenuKb
from keyboards.inline.inline_keyboard import LessonsIKb, LessonsCBData
from routers.private_chat.private_chat import router
from settings import global_storage
from states import LessonsStates
from utils.module.message_tool import get_message_id_with_list_photo, CashingSendPhotos
from utils.mysql import Replacements, GlobalValues


async def _get_subscribe_message_text(telegram_id: Optional[int]):
    if Replacements().get_subscription_status(telegram_id):
        return 'Ти також можеш відписатися від майбутніх розсилках замін, написавши /unsubscribe'
    return 'Ти також можеш підписатися на розсилку нових замін, написавши /subscribe'


@router.message(
    Text(text=LessonsKb.replacements_btn),
    StateFilter(LessonsStates.main_menu)
)
async def get_photo_with_replacements(message: types.Message):
    """Отримуємо фото замін, які в нас присутні"""
    upload_message_text = '⏳ Одну хвилинку, шукаю заміни...🖼'
    file_no_found_message_text = 'Замін немає'
    fail_send_message_text = 'Не вдалося зібрати всі фото через негідника, котрий зберіг ці заміни'

    caching = CashingSendPhotos(message=message, redis=global_storage, key='replacements')
    notification_upload_message, list_messages_of_send = await caching.get_photo(
        dir_path=config.PATH_TO_PHOTO_REPLACEMENTS,
        upload_photo_text=upload_message_text,
        file_no_found_text=file_no_found_message_text,
        fail_send_text=fail_send_message_text
    )
    # Отримуємо потрібну інформацію для коректної роботи кнопок отримати заміни з сайту і навпаки

    list_message_id = await get_message_id_with_list_photo(list_message=list_messages_of_send)
    coding_text = list_message_id
    if isinstance(list_message_id, list):
        coding_text = f'{list_message_id[0]}_{list_message_id[-1]}'

    from handlers.group_admin.message.verification_replacements import get_text_for_username_in_replacements
    caption = ''
    if list_messages_of_send:
        caption = await get_text_for_username_in_replacements(username=GlobalValues().get('username_in_replacements'))
    # send message with sub text and reply_inline_kb
    await message.answer(
        text=f'{await _get_subscribe_message_text(telegram_id=message.chat.id)}\n{caption}',
        reply_markup=LessonsIKb().get_replacements(
            f'{notification_upload_message.message_id}|{coding_text}'
        )
    )
    # Remove message about download file
    await notification_upload_message.delete()


@router.callback_query(
    LessonsCBData.filter(),
    StateFilter(LessonsStates.main_menu)
)
async def inline_menu_get_replacements(query: CallbackQuery, callback_data: LessonsCBData, bot: aiogram.Bot):
    logging.info('Show replacements with site')
    match callback_data.type_inl_btn:
        case 'see_with_site':
            process_download_message_id = callback_data.message_id.split('|')[0]
            photo_message_id = callback_data.message_id.split('|')[1].split('_')
            if isinstance(photo_message_id, str):
                photo_message_id = (photo_message_id,)
            elif isinstance(photo_message_id, list):
                photo_message_id = tuple(map(int, photo_message_id))
                photo_message_id = (message_id for message_id in range(photo_message_id[0], photo_message_id[-1] + 1))

            list_message_id = (
                process_download_message_id,
                *photo_message_id,
                query.message.message_id
            )
            await _remove_old_message(chat_id=query.message.chat.id, list_message_id=list_message_id, bot=bot)
            await _get_replacements_from_site(query=query, callback_data=callback_data)

        case 'see_photo':
            list_message_id = (
                callback_data.message_id,
                query.message.message_id
            )
            await _remove_old_message(chat_id=query.message.chat.id, list_message_id=list_message_id, bot=bot)
            await get_photo_with_replacements(message=query.message)

    await query.answer(cache_time=0)


@cache(10)
def create_message_for_replacements_with_site(name_group: Optional[str | None]) -> Optional[str]:
    """Отримання замін з БД, які на сайті"""

    info_of_replacements = Replacements().get_info_replacements_with_table()

    news_of_replacements = Replacements().get_news_replacements_with_table()

    all_my_replacements = Replacements().get_all_replacements_for_group_with_table(name_group=name_group)

    all_my_replacements_txt = 'Замін немає'
    if len(all_my_replacements) and not all_my_replacements[0] is None:
        all_my_replacements_txt = ''
        for item in all_my_replacements:
            all_my_replacements_txt += '{}\n'.format(' '.join(item))

    if not news_of_replacements:
        news_of_replacements = ['Немає']

    name_group_text = name_group
    if name_group is None:  # якщо група не вказана у користувача
        name_group_text = 'Група не вказана'
        all_my_replacements_txt = f'Замін немає, так як ти вказав свою групу.\n\n' \
                                  f'Щоб вказати свою групу перейди в /menu\n' \
                                  f'{MainMenuKb.lessons_btn} > {LessonsKb.settings_btn}\n' \
                                  f'або напиши команду /setting_replacements'

    message_text = "{0}:\n{1}\n\nОголошення:\n{2}\n\nЗаміни:\n{3}"
    return message_text.format(
        name_group_text, '\n'.join(info_of_replacements), ''.join(news_of_replacements), all_my_replacements_txt
    )


async def _get_replacements_from_site(query: CallbackQuery, callback_data: LessonsCBData):
    logging.debug('Click on inline button with inline_keyboard for get type replacements')

    name_group = Replacements().get_subscription_name_group(telegram_id=query.from_user.id)
    replacements_from_site_message_text = create_message_for_replacements_with_site(
        name_group=name_group)

    # Send message with replacements from site
    replacements_from_site = await query.message.answer(replacements_from_site_message_text)

    # Get message_id message about replacements from site, where in future will remove message
    replacements_from_site_message_id = await get_message_id_with_list_photo(list_message=replacements_from_site)

    await query.message.answer(
        text=await _get_subscribe_message_text(telegram_id=query.from_user.id),
        reply_markup=LessonsIKb().get_replacements(
            message_id=replacements_from_site_message_id,
            inline_callback_text=callback_data.type_inl_btn
        )
    )


async def _remove_old_message(chat_id: Optional[int], list_message_id: Optional[tuple], bot: aiogram.Bot):
    # Remove old message
    for message_id in list_message_id:
        try:
            await bot.delete_message(
                chat_id=chat_id,
                message_id=message_id
            )
        except Exception as error:
            pass
