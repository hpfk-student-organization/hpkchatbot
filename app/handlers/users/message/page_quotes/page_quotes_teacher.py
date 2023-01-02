# переглядаємо список викладачів, переходимо між сторінками, вибираємо викладача і переглядаємо його цитату
import math
import random

from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext

from keyboards.default import QuotesTeacherKb
from routers.private_chat.private_chat import router
from states import QuotesTeacherStates
from utils.mysql import QuotesTeacher
from utils.tools import sort


def __remove_last_quotes_with_list_quotes(list_quotes: list) -> tuple[list, str]:
    """
        Копіює list, як новий об'єкт, і видаляє останній елемент. Потрібен для коректної роботи алгоритму підбору цитат

    Args:
        list_quotes: список цитат

    Returns: Новий список, який менше попереднього на 1 елемент, видалений елемент

    """
    list_quotes_copy = list_quotes.copy()  # копіюємо список, щоб це був інший об'єкт
    remove_quotes = list_quotes_copy.pop()  # видалимо останній елемент, при цьому повернемо цей елемент.
    return list_quotes_copy, remove_quotes


def __get_new_list():
    """
    Отримуємо список з фразами
    @return: list()
    """
    return [
        'Я сказав, ж нічого!',
        '😑',
        'Повторяю ще раз, там нічого немає!', '-_-',
        'Ну і для кого це я розповідаю 🧐',
        'Як ти плануєш туди перейти? Там ж нічого немає)',
        'Ти робиш ВЕЛИКУ помилку!',
        'БІП.БУП.БУП.БІП',
        'Такої наполегливі нехватає на парі в Сівка',
        'І довго ми тут будемо пробувати руйнувати логіку Всесвіту? 🤓',
        'Error 404',
        'Я зрозумів, це буде довго...',
        'Яка чудова погода!'
    ]


async def __get_random_jocker_text(state: FSMContext, first: str = None) -> str:
    """

    Текст, який появляється, якщо спробувати перейти за край списку

    @param state:
    @param first:
    @return:
    """

    user_data = await state.get_data()
    list_jokers = user_data.get('list_jokers', None)
    if not list_jokers:  # if result is none
        list_jokers = __get_new_list()
        await state.update_data(list_jokers=list_jokers)
        if first:
            return first

    if not list_jokers[:-1]:
        await state.update_data(list_jokers=__get_new_list())
        return list_jokers[-1]

    random.shuffle(list_jokers)
    await state.update_data(list_jokers=list_jokers[:-1])
    return list_jokers[-1]


# перехід між сторінками

@router.message(
    Text(text=QuotesTeacherKb.next_btn),
    StateFilter(QuotesTeacherStates.main_menu),
)
async def next_page_button(message: types.Message, state: FSMContext):
    """При переході на наступну сторінку"""
    user_data = await state.get_data()
    list_all_teachers = list(sort(QuotesTeacher().select_all_list_teachers()))
    level_page_quotes = user_data.get("level_page_quotes")
    last_page_quotes = math.ceil(len(list_all_teachers) / 4)
    if level_page_quotes >= last_page_quotes:
        # якщо ми вже на останній сторінці
        message_text = await __get_random_jocker_text(state=state, first='Там нічого немає, чуєш нічого!')
        await message.answer(text=message_text)
        return

    message_text = f"Ти на {level_page_quotes + 1} сторінці"
    await message.answer(
        text=message_text,
        reply_markup=QuotesTeacherKb.main_menu(
            list_all_teachers=list_all_teachers,
            number_page=level_page_quotes + 1
        )
    )
    await state.update_data(level_page_quotes=level_page_quotes + 1)


@router.message(
    Text(text=QuotesTeacherKb.last_btn),
    StateFilter(QuotesTeacherStates.main_menu),
)
async def last_page_button(message: types.Message, state: FSMContext):
    """При переході на попередню сторінку"""
    user_data = await state.get_data()
    # list_all_teachers = list(sort(QuotesTeacher().select_all_list_teachers(), key_list=language.UA_RUS_EN))
    list_all_teachers = list(sort(QuotesTeacher().select_all_list_teachers()))
    level_page_quotes = user_data.get("level_page_quotes")

    if level_page_quotes <= 1:
        # If user on first page
        message_text = await __get_random_jocker_text(state=state, first='Там нічого немає, чуєш нічого!')
        await message.answer(text=message_text)
        return

    message_text = f"Ти на {level_page_quotes - 1} сторінці"
    await message.answer(
        text=message_text,
        reply_markup=QuotesTeacherKb.main_menu(
            list_all_teachers=list_all_teachers,
            number_page=level_page_quotes - 1
        )
    )
    await state.update_data(level_page_quotes=level_page_quotes - 1)


@router.message(
    StateFilter(QuotesTeacherStates.main_menu) and Text(endswith=list(QuotesTeacher().select_all_list_teachers())),

)
async def click_to_teacher_button(message: types.Message, state: FSMContext):
    """Натиснемо на кнопку з викладачем"""
    name_teacher_split: list = message.text.split(' ')

    if len(name_teacher_split)==2:
        name_teacher = name_teacher_split[1]
    else:
        name_teacher = name_teacher_split[0]
    # отримуємо цитати, яку видалили. Список перед тим був в типом set - тобто не впорядкований
    list_quotes = QuotesTeacher().select_all_quotes_with_teacher(name_teacher)

    # отримаємо одну цитату і видалимо її
    new_list_quotes, quotes = __remove_last_quotes_with_list_quotes(list_quotes)

    # запишемо для ключа teacher нашого викладача
    # запишемо список цитат цього викладача
    await state.update_data(teacher=name_teacher, list_quotes=new_list_quotes)

    message_text = f"Цитата:\n" \
                   f"« {quotes} » ({name_teacher})"

    await message.answer(
        text=message_text,
        reply_markup=QuotesTeacherKb.quotes()
    )

    await state.set_state(QuotesTeacherStates.view_quotes)


@router.message(
    Text(text=QuotesTeacherKb.repeat_btn),
    StateFilter(QuotesTeacherStates.view_quotes),
)
async def click_to_view_button(message: types.Message, state: FSMContext):
    """Кнопка - переглянути ще раз"""
    user_data = await state.get_data()
    teacher = user_data.get("teacher")
    list_quotes = user_data.get("list_quotes")
    if not list_quotes:
        # якщо список none
        list_quotes = QuotesTeacher().select_all_quotes_with_teacher(teacher)

    new_list_quotes, quotes = __remove_last_quotes_with_list_quotes(list_quotes)  # отримаємо одну цитату і видалимо її
    await state.update_data(list_quotes=new_list_quotes)

    message_text = f"Цитата:\n" \
                   f"« {quotes} » ({teacher})"

    await message.answer(
        text=message_text,
        # reply_markup=QuotesTeacherIKb.quotes()
    )
