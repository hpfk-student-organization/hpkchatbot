from loguru import logger
from datetime import datetime
from typing import Optional

from aiogram import types, F
from aiogram.fsm.context import FSMContext

import config
from keyboards.default import LessonsKb, MainMenuKb, ForStudentsKb, AnonymousChatKb, QuotesTeacherKb
from routers.private_chat.private_chat import router
from states import LessonsStates, ForStudentsStates, QuotesTeacherStates, AnonymousChatStates
from utils.mysql import QuotesTeacher, AnonimChat
from utils.tools import sort


@router.message(F.text == MainMenuKb.lessons_btn)
async def lessons_button(message: types.Message, state: FSMContext):
    """При переході в розділ lesson"""
    menu_text = "Що хочеш дізнатися?"
    await message.answer(
        text=menu_text,
        reply_markup=LessonsKb.main_menu()
    )

    await state.set_state(LessonsStates.main_menu)


@router.message(F.text == MainMenuKb.for_students_btn)
async def for_students_button(message: types.Message, state: FSMContext):
    """При переході в розділ for_students"""
    menu_text = "Що хочеш дізнатися?"
    await message.answer(
        text=menu_text,
        reply_markup=ForStudentsKb.main_menu()
    )
    await state.set_state(ForStudentsStates.main_menu)


@router.message(F.text == MainMenuKb.quotes_btn)
async def quotes_button(message: types.Message, state: FSMContext,
                        level_page_quotes: Optional[int] = 1,
                        menu_text: Optional[str] = "Що хочеш дізнатися?"):
    """При переході в розділ quotes_page"""

    await message.answer(
        text=menu_text,
        reply_markup=QuotesTeacherKb.main_menu(
            list_all_teachers=list(sort(QuotesTeacher().select_all_list_teachers())),
            number_page=level_page_quotes)
    )
    await state.update_data(level_page_quotes=level_page_quotes)  # встановимо номер сторінки на якій ми знаходимося
    await state.set_state(QuotesTeacherStates.main_menu)


@router.message(F.text == MainMenuKb.ads_btn)
async def ads_button(message: types.Message, state: FSMContext):
    """При переході в розділ ads_btn"""

    menu_text = "Що хочеш дізнатися?"
    from handlers.users.message.lessons.parssing.schedule import read_excel
    import os
    read_excel(os.path.join(config.PATH_TO_FILE_SCHEDULE, '20220825_134745-2.xlsx'))
    read_excel(os.path.join(config.PATH_TO_FILE_SCHEDULE, 'file.xlsx'))
    """for i in range(1, 100):
        print(abc(i), i)
"""
    await message.answer(
        text=menu_text
    )
    # await state.set_state(QuotesTeacherStates.main_menu)


@router.message(F.text == MainMenuKb.anonymous_chat_btn)
async def anonymous_chat_button(message: types.Message, state: FSMContext):
    """При переході в розділ anonymous_btn"""

    from utils.module.weather import Weather
    weather = Weather(config.WEATHER_TOKEN, city='Хмельницкий')

    start_time = datetime.now()
    message_text = "Що хочеш дізнатися? {0}".format(weather.get_detailed_status(emoji=True))
    logger.debug(datetime.now() - start_time)

    if not AnonimChat().is_check_exist_user(telegram_id=message.from_user.id):
        message_text = "👋 Привіт!\n\n" \
                       "В цьому розділі ти можеш найти собі анонімного співрозмовника в анонімному чаті\n\n" \
                       "Натискай на кнопку внизу, а там розберемося\n\nСпонсор цього бота є " \
                       "https://instagram.com/kr_hpfk"
        AnonimChat().add_new_user(telegram_id=message.from_user.id)

    await message.answer(
        text=message_text,
        reply_markup=AnonymousChatKb.main_menu()
    )

    await state.set_state(AnonymousChatStates.main_menu)


# @router.message()
async def welcome(message: types.Message, state: FSMContext):
    from keyboards.default.default_keyboard import LessonsKb
    await message.answer(text=message.text, reply_markup=LessonsKb.main_menu())
    # await state.set_state(ExampleState1.example_state_3)
    # print(message.chat.type)
    """#await state.update_data(test=message.text)
    user_data = await state.get_data()
    print(user_data.get("test", 0))
    await message.answer(text=str(user_data.get("test", 0)))"""
    # await message.delete()
