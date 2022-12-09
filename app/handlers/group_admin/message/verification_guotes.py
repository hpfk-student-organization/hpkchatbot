# перевіряємо нові цитати

import aiogram
from aiogram import types, exceptions
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType

from filters.check_callback_data import CheckCallbackMessageFilter
from filters.content_types import ContentTypesFilter
from keyboards.inline.inline_keyboard import VerificationQuotesCBData, VerificationQuotesIKb
from routers.group_chat.for_admin import router
from utils.mysql import QuotesTeacher


@router.callback_query(VerificationQuotesCBData.filter(), StateFilter('*'))
async def inline_menu_verif_new_quotes(query: CallbackQuery, callback_data: VerificationQuotesCBData, bot: aiogram.Bot,
                                       state: FSMContext):
    levels = {
        1: select_variant_correct_quotes,
        2: click_to_inl_btn_send_feed_back,

    }
    current_level_function = levels[callback_data.level]
    await current_level_function(callback=query, bot=bot,
                                 type_inl_btn=callback_data.type_inl_btn, user_id=callback_data.user_id,
                                 message_id_in_data=callback_data.message_id,
                                 text_quotes_and_teacher=query.message.text.split('\n')[1],
                                 message_id_send_btn=callback_data.message_id_send_btn)
    await query.answer(cache_time=0)


async def select_variant_correct_quotes(callback: types.CallbackQuery,
                                        bot: aiogram.Bot,
                                        type_inl_btn: str,
                                        user_id: int,
                                        text_quotes_and_teacher: str,
                                        message_id_in_data: int,
                                        message_id_send_btn: int,
                                        **kwargs):
    """Коли ми вибираємо чи цитату зберігати, чи ні"""
    if type_inl_btn == VerificationQuotesIKb.feedback_inline_callback[1]:
        """Натиснемо назад"""

        await callback.message.edit_text(
            text='\n'.join(callback.message.text.split('\n')[:-2]),
            reply_markup=VerificationQuotesIKb().send_feed_back(
                user_id=user_id,
                message_id=message_id_in_data,
            )
        )
        return

    save_quotes_text = "збережено"
    callback_text = "Loading..."

    if type_inl_btn == VerificationQuotesIKb.verification_inline_callback[0]:  # зберігаємо цитату
        text_quotes, text_teacher = [text.strip() for text in text_quotes_and_teacher.split('-') if text not in '«»-']
        text_quotes: str = text_quotes.strip('«» ')
        if not QuotesTeacher().is_check_exist_teacher(teacher=text_teacher):
            # if teacher not exist
            print(QuotesTeacher().is_check_exist_teacher(teacher=text_teacher))
            await callback.answer(
                text='❗️Цитата не може бути збережена, так як даний викладач невідомий',
                show_alert=True,
            )
            return
        QuotesTeacher().add_new_quotes(
            teacher=text_teacher,
            text=text_quotes
        )
        callback_text = 'Цитата збережена до загального списку',

    elif type_inl_btn == VerificationQuotesIKb.verification_inline_callback[2]:  # цитата вірна
        callback_text = 'Сповіщення надіслано: "Цитата збережена"',

    elif type_inl_btn == VerificationQuotesIKb.verification_inline_callback[1]:  # не зберігати
        callback_text = 'Сповіщення надіслано: "Цитата не збережена"',
        save_quotes_text = f"не {save_quotes_text}"

    message_text = f"Цитата перевірена.\n" \
                   f"Результат: {save_quotes_text}\n\n" \
                   f"{text_quotes_and_teacher}"
    try:
        message = await bot.send_message(
            chat_id=user_id,
            text=message_text
        )  # відправимо повідомлення користувачу, який відправив цитату
        await callback.message.edit_reply_markup(
            reply_markup=VerificationQuotesIKb().send_feed_back(
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


async def click_to_inl_btn_send_feed_back(callback: types.CallbackQuery,
                                          user_id: int,
                                          message_id_in_data: int,
                                          **kwargs):
    """Натиснемо кнопку залишити відгук"""
    message_text = f"{callback.message.text}\n\n" \
                   f"Щоб залишити відгук на цитату - потрібно відповісти на повідомлення"
    await callback.message.edit_text(
        text=message_text,
        reply_markup=VerificationQuotesIKb().back(
            user_id=user_id,
            message_id=message_id_in_data,
        )
    )


@router.message(
    lambda message: message.reply_to_message,
    CheckCallbackMessageFilter(VerificationQuotesCBData.__prefix__),
    ContentTypesFilter(ContentType.TEXT),
    StateFilter('*'),
)
async def reply_feed_back(message: types.Message, bot: aiogram.Bot, **kwargs):
    """Коли хтось з Administrator залишає відгук"""

    list_callback = message.reply_to_message.reply_markup.inline_keyboard[0][0].callback_data.split(':')
    user_id, reply_message_id = list_callback[-3:-1]

    message_text = f"Відгук на вашу цитату:\n" \
                   f"{message.text}"
    await bot.send_message(
        chat_id=user_id,
        text=message_text,
        reply_to_message_id=reply_message_id
    )


