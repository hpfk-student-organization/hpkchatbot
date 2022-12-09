# перевіряємо нові цитати
import datetime
import logging
from typing import Optional, List

import aiogram
from aiogram import types, exceptions
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType

import config
from filters.check_callback_data import CheckCallbackMessageFilter
from filters.content_types import ContentTypesFilter
from keyboards.inline.inline_keyboard import VerificationReplacementsCBData, VerificationReplacementsIKb
from routers.group_chat.for_admin import router
from utils.module.message_tool import get_media_album_with_list_file_id
from utils.mysql import MediaFileID, Replacements, GlobalValues


@router.callback_query(VerificationReplacementsCBData.filter(), StateFilter('*'))
async def inline_menu_verif_new_quotes(query: CallbackQuery, callback_data: VerificationReplacementsCBData,
                                       state: FSMContext, bot: aiogram.Bot):
    levels = {
        1: select_variant_correct_quotes,
        2: click_to_inl_btn_send_feed_back,

    }

    current_level_function = levels[callback_data.level]
    await current_level_function(callback=query, bot=bot,
                                 type_inl_btn=callback_data.type_inl_btn, user_id=callback_data.user_id,
                                 message_id_in_data=callback_data.message_id,
                                 message_id_message=query.message.message_id,
                                 show_information_user=callback_data.show_information_user,
                                 message_id_send_btn=callback_data.message_id_send_btn,
                                 )
    print(callback_data)
    await query.answer(cache_time=0)


async def select_variant_correct_quotes(callback: types.CallbackQuery,
                                        bot: aiogram.Bot,
                                        type_inl_btn: str,
                                        user_id: int,
                                        show_information_user: bool,
                                        message_id_message: int,
                                        message_id_in_data: int,
                                        message_id_send_btn: int,
                                        **kwargs):
    """Коли ми вибираємо чи цитату зберігати, чи ні"""

    if type_inl_btn == VerificationReplacementsIKb.feedback_inline_callback[1]:
        """Натиснемо назад"""

        await callback.message.edit_text(
            text='\n'.join(callback.message.text.split('\n')[:-2]),
            reply_markup=VerificationReplacementsIKb().send_feed_back(
                user_id=user_id,
                message_id=message_id_in_data,
            )
        )
        return

    save_quotes_text = "збережено"
    callback_text = "Loading..."

    if type_inl_btn == VerificationReplacementsIKb.verification_inline_callback[0]:  # send and save
        list_file_id, username,  = MediaFileID().get_file_id_replacements(message_id_message)

        username: str = username[0]
        await save_photo_replacements_in_file_storage(bot=bot, list_file_id=list_file_id)

        username_with_databases = await save_username(username=username, show_username=show_information_user)

        caption_text = f"Нові заміни станом {datetime.datetime.now().strftime('%H:%M')}\n"

        caption_text += await get_text_for_username_in_replacements(username_with_databases)
        media_album = await get_media_album_with_list_file_id(list_file_id=list_file_id, caption=caption_text)
        user_sub = Replacements().get_subscription_who_get_photo()

        await send_media_album_for_user(bot=bot, list_user_sub=user_sub, media=media_album)
        Replacements().update_last_time_send_replacements(1)

        callback_text = 'Заміни збережені та відправленні підписникам'

    elif type_inl_btn == VerificationReplacementsIKb.verification_inline_callback[1]:  # correct
        list_file_id, username = MediaFileID().get_file_id_replacements(message_id_message)
        await save_photo_replacements_in_file_storage(bot=bot, list_file_id=list_file_id)
        await save_username(username=username, show_username=show_information_user)

        callback_text = 'Сповіщення надіслано: "Заміни тільки збережені"'

    elif type_inl_btn == VerificationReplacementsIKb.verification_inline_callback[2]:  # не зберігати
        callback_text = 'Сповіщення надіслано: "Заміни не збережені"'
        save_quotes_text = f"не {save_quotes_text}"
    message_text = f"Заміни перевірені.\n" \
                   f"Результат: {save_quotes_text}\n\n" \
                   f"{''}"

    MediaFileID().delete_file_id_in_replacements(message_id=message_id_message)
    try:
        message = await bot.send_message(
            chat_id=user_id,
            text=message_text,
            reply_to_message_id=message_id_send_btn
        )  # відправимо повідомлення користувачу, який відправив заміни
        await callback.message.edit_reply_markup(
            reply_markup=VerificationReplacementsIKb().send_feed_back(
                user_id=user_id,
                message_id=message.message_id,
            )
        )
        await callback.answer(
            text=callback_text
        )
        return
    except exceptions.TelegramForbiddenError:
        await callback.answer(text='Користувач заблокував бота')

    await callback.message.edit_reply_markup()


async def get_text_for_username_in_replacements(username: Optional[str]) -> Optional[str]:
    if username:
        return f"Поділився з усіма нами @{username}"
    return ''


async def click_to_inl_btn_send_feed_back(callback: types.CallbackQuery,
                                          user_id: int,
                                          message_id_in_data: int,
                                          **kwargs):
    """Натиснемо кнопку залишити відгук"""
    message_text = f"{callback.message.text}\n\n" \
                   f"Щоб залишити відгук на заміни - потрібно відповісти на повідомлення"
    await callback.message.edit_text(
        text=message_text,
        reply_markup=VerificationReplacementsIKb().back(
            user_id=user_id,
            message_id=message_id_in_data,
        )
    )


async def save_photo_replacements_in_file_storage(bot: aiogram.Bot, list_file_id: List[str]):
    """Saving photo in file system for open replacements"""
    from utils.tools import remove_file_in_dir
    # remove file in dir, for save new photo
    await remove_file_in_dir(config.PATH_TO_PHOTO_REPLACEMENTS)

    for file_id in list_file_id:
        logging.debug(file_id)
        file = await bot.get_file(file_id)
        await bot.download_file(
            file_path=file.file_path,
            destination='{0}{1}_{2}.jpg'.format(
                config.PATH_TO_PHOTO_REPLACEMENTS, file.file_id, datetime.datetime.now().strftime('%H_%M_%S_%f')
            )
        )


async def save_username(username: Optional[str], show_username: Optional[bool]):
    # Save username in databases
    key = 'username_in_replacements'
    if not show_username:
        username = None

    if GlobalValues().exist(name=key):
        GlobalValues().update(name=key, value=username)
        return username

    GlobalValues().add(name=key, value=username)
    return username


@router.message(
    lambda message: message.reply_to_message,
    CheckCallbackMessageFilter(VerificationReplacementsCBData.__prefix__),
    ContentTypesFilter(ContentType.TEXT),
    StateFilter('*'),
)
async def reply_feed_back(message: types.Message, bot: aiogram.Bot, **kwargs):
    """Коли хтось з Administrator залишає відгук"""

    list_callback = message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split(':')
    user_id, reply_message_id = list_callback[-4:-2]

    message_text = f"Відгук на ваші заміни:\n" \
                   f"{message.text}"
    await bot.send_message(
        chat_id=user_id,
        text=message_text,
        reply_to_message_id=reply_message_id
    )


async def send_media_album_for_user(
        bot: aiogram.Bot, list_user_sub: List[int | str],
        media: List
):
    """
    Додає в чергу на відправлення повідомлень(замін) для розсилки. Так, як Bot API має ліміти на відправлення
    повідомлень в різні чати(30 штук на 1 секунду), використовуємо Черги, завдяки якій ми задаємо частоту виконання
    команди.

    :param bot:
    :param list_user_sub: список користувачів, яким потрібно надіслати повідомлення
    :param media: список самих фото

    """
    from scheduler.private_chat import queue, scheduler, jobs_id
    scheduler.resume_job(jobs_id[0])
    for user_id in list_user_sub:
        await queue.put(
            bot.send_media_group(
                chat_id=user_id,
                media=media
            )
        )

