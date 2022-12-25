# додаємо нові цитати
from loguru import logger

import aiogram
from aiogram import types, F
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, ContentType

import config
from filters.content_types import ContentTypesFilter
from keyboards.default import QuotesTeacherKb
from keyboards.inline.inline_keyboard import SendNewQuotesIKb, SendNewQuotesCBData, VerificationQuotesIKb
from routers.private_chat.private_chat import router
from states import QuotesTeacherStates


# далі додаємо цитати для викладачів
@router.message(
    Text(text=QuotesTeacherKb.send_quotes_btn),
    StateFilter(QuotesTeacherStates.main_menu)
)
async def group_add_to_new_quotes_button(message: types.Message, state: FSMContext):
    """Вибираємо літеру з якої починається викладач"""

    message_text = f"Щоб продовжити, заповніть наступні дані"
    await message.answer(
        text=message_text,
        reply_markup=QuotesTeacherKb.back()
    )
    message_text = f"Виберіть викладача із списку, для якого плануєте додати цитату, або напишіть його\n" \
                   f"\n" \
                   f""
    await message.answer(
        text=message_text,
        reply_markup=SendNewQuotesIKb().first_letter_with_all_teacher_in_send_new_quotes()
    )
    await state.set_state(QuotesTeacherStates.select_teacher)


@router.callback_query(SendNewQuotesCBData.filter(),
                       StateFilter(QuotesTeacherStates.select_teacher))
async def inline_menu_add_quotes(
        query: CallbackQuery, callback_data: SendNewQuotesCBData, state: FSMContext, bot: aiogram.Bot):
    logger.debug('Click on inline button with inline_keyboard for select teacher')
    levels = {
        0: group_add_to_new_quotes_button_first_letter,
        1: group_add_to_new_quotes_button_get_all_teacher_with_first_letter,
        2: select_teachers,
    }
    current_level_function = levels[callback_data.level]
    await current_level_function(query, first_letter=callback_data.first_letter, teacher=callback_data.teacher,
                                 state=state, bot=bot)
    await query.answer(cache_time=0)


async def group_add_to_new_quotes_button_first_letter(callback: types.CallbackQuery, **kwargs):
    """Вибираємо літеру з якої починається викладач"""

    message_text = f"Виберіть викладача із списку, для якого плануєте додати цитату, " \
                   f"або напишіть\n" \
                   f"\n" \
                   f""

    await callback.message.edit_text(
        text=message_text,
        reply_markup=SendNewQuotesIKb().first_letter_with_all_teacher_in_send_new_quotes()
    )


async def group_add_to_new_quotes_button_get_all_teacher_with_first_letter(
        callback: types.CallbackQuery,
        first_letter: str, **kwargs
):
    """Змінюємо клавіатуру на клавіатуру з викладачами"""

    message_text = f"Виберіть викладача із списку, для якого плануєте додати цитату, " \
                   f"або напишіть, якщо такого немає\n" \
                   f"\n" \
                   f""
    await callback.message.edit_text(
        text=message_text,
        reply_markup=SendNewQuotesIKb().all_teacher_in_letter_send_new_quotes(first_letter=first_letter)
    )


async def select_teachers(callback: types.CallbackQuery, teacher: str, state: FSMContext, bot: aiogram.Bot, **kwargs):
    """Якщо ми вибрали викладача із клавіатури"""

    await callback.message.delete()  # видалимо повідомлення з клавіатурою з вибором викладачів

    message_text = f"Напишіть цитату для викладача {teacher}"
    await state.update_data(teacher=teacher)
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text=message_text,
        reply_markup=QuotesTeacherKb.back()
    )
    await state.set_state(QuotesTeacherStates.add_new_quotes)


@router.message(
    ~(F.text == QuotesTeacherKb.back_btn),
    ContentTypesFilter(ContentType.TEXT),
    StateFilter(QuotesTeacherStates.select_teacher),
)
async def input_new_quotes(message: types.Message, state: FSMContext):
    """Якщо ми вибрали викладача із клавіатури"""
    teacher = message.text
    if message.text == QuotesTeacherKb.back_btn:  # перевірка для того, щоб знати, чи викликати функцію чи ні
        user_data = await state.get_data()
        teacher = user_data.get('teacher', 'Невідомо')

    message_text = f"Напишіть цитату для викладача {teacher}"
    await state.update_data(teacher=teacher)
    await message.answer(
        text=message_text,
        reply_markup=QuotesTeacherKb.back()
    )
    await state.set_state(QuotesTeacherStates.add_new_quotes)


@router.message(
    ~(F.text == QuotesTeacherKb.back_btn),
    ContentTypesFilter(ContentType.TEXT),
    StateFilter(QuotesTeacherStates.add_new_quotes),
)
async def save_new_quotes(message: types.Message, state: FSMContext):
    """Якщо надіслати цитату написану з клавіатури"""
    user_data = await state.get_data()
    teacher = user_data.get('teacher', 'Невідомо')

    quotes = message.text
    zip_quotes = f"« {quotes} » - {teacher}"
    message_text = f"Цитата записана: {zip_quotes}\n" \
                   f"\n"
    await state.update_data(new_quotes=quotes)
    await message.answer(
        text=message_text,
        reply_markup=QuotesTeacherKb.send_quotes()
    )
    await state.set_state(QuotesTeacherStates.send_quotes)


@router.message(
    Text(text=QuotesTeacherKb.send_btn),
    StateFilter(QuotesTeacherStates.send_quotes))
async def send_new_quotes_for_verification(message: types.Message, state: FSMContext, bot:aiogram.Bot):
    """Надсилаємо цитату для перевірки"""
    user_data = await state.get_data()
    teacher = user_data.get('teacher', 'Невідомо')
    new_quotes = user_data.get('new_quotes', 'Невідомо')

    text_quotes = f"« {new_quotes} » - {teacher}"
    message_text = f"Цитата відправлена на перевірку\n" \
                   f"{text_quotes}"
    zip_quotes = f"Цитата:\n" \
                 f"{text_quotes}"

    try:
        # Send quotes the verification in group admin
        await bot.send_message(
            chat_id=config.ID_GROUP_ADMIN,
            text=zip_quotes,
            reply_markup=VerificationQuotesIKb().verification(user_id=message.from_user.id,
                                                              message_id_send_btn=message.message_id)
        )
        # Double message in private message
        await message.answer(
            text=message_text
        )

        from handlers.users.message.back import back_to_page_teacher_button
        await back_to_page_teacher_button(message=message, state=state)
        # Exit with function
        return
    except Exception as error:
        logger.error(f"{error}, when bot try send quotes in admin chat. Try edit id_group for admin. "
                      f"Not correct ID - '{config.ID_GROUP_ADMIN}'")

    message_test_about_fail_send_quotes = "Нажаль, цитату не вдалося надіслати на перевірку. " \
                                          "Попробуй надіслати цитату пізніше."
    await message.answer(
        text=message_test_about_fail_send_quotes
    )
