from loguru import logger

from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext

from keyboards.default import QuotesTeacherKb, LessonsKb, AnonymousChatKb
from routers.private_chat.private_chat import router
from states import LessonsStates, ForStudentsStates, ADSStates, AnonymousChatStates, QuotesTeacherStates
from utils.mysql import MediaFileID


@router.message(
    Text(text=QuotesTeacherKb.back_btn),
    StateFilter(None)
)
@router.message(
    Text(text=QuotesTeacherKb.back_btn),
    StateFilter(LessonsStates.main_menu,
                ForStudentsStates.main_menu,
                ADSStates.main_menu,
                AnonymousChatStates.main_menu,
                QuotesTeacherStates.main_menu)
)
async def back_to_main_menu_button(message: types.Message, state: FSMContext):
    """Користувач тисне кнопку back і повертається на головне меню"""
    from handlers.users.commands import command_main_menu
    await command_main_menu(message=message, state=state)


@router.message(
    Text(text=QuotesTeacherKb.back_btn),
    StateFilter(QuotesTeacherStates.view_quotes, QuotesTeacherStates.select_teacher)
)
async def back_to_page_teacher_button(message: types.Message, state: FSMContext):
    """Повернемося до сторінок цитат"""
    from handlers.users.message.main import quotes_button

    user_data = await state.get_data()
    level_page_quotes = user_data.get("level_page_quotes", 1)
    await quotes_button(
        message=message,
        state=state,
        level_page_quotes=level_page_quotes,
        menu_text=f"Ти на {level_page_quotes} сторінці"
    )


@router.message(
    Text(text=QuotesTeacherKb.back_btn),
    StateFilter(QuotesTeacherStates.add_new_quotes)
)
async def back_to_page_select_teacher_button(message: types.Message, state: FSMContext):

    from handlers.users.message.page_quotes.add_new_quotes import group_add_to_new_quotes_button
    await group_add_to_new_quotes_button(message=message, state=state)


@router.message(
    Text(text=QuotesTeacherKb.back_btn),
    StateFilter(QuotesTeacherStates.send_quotes)
)
async def back_to_input_quotes(message: types.Message, state: FSMContext):
    """Коли ми хочемо відредагувати цитату"""
    from handlers.users.message.page_quotes.add_new_quotes import input_new_quotes
    await input_new_quotes(message=message, state=state)


@router.message(
    Text(text=LessonsKb.back_btn),
    StateFilter(LessonsStates.send_new_replacements)
)
async def back_to_lesson_main_menu_with_remove_tmp_file(message: types.Message, state: FSMContext):
    """Коли ми хочемо повернутися в головне меню сторінки Lesson, та видалити за собою фото, які раніше відсилалися"""
    logger.debug("Remove file_id with databases")
    MediaFileID().delete(telegram_id=message.from_user.id, type_file_id='replacement')

    from handlers.users.message.main import lessons_button
    await lessons_button(message=message, state=state)


@router.message(
    Text(text=LessonsKb.back_btn),
    StateFilter(LessonsStates.menu_settings)
)
async def back_to_lesson_main_menu(message: types.Message, state: FSMContext):
    """Коли ми хочемо повернутися в головне меню сторінки Lesson"""

    from handlers.users.message.main import lessons_button
    await lessons_button(message=message, state=state)


@router.message(
    Text(text=AnonymousChatKb.back_btn),
    StateFilter(AnonymousChatStates.settings)
)
async def back_to_lesson_main_menu(message: types.Message, state: FSMContext):
    """Коли ми хочемо повернутися в головне меню сторінки Anonymous"""

    from handlers.users.message.main import anonymous_chat_button
    await anonymous_chat_button(message=message, state=state)
