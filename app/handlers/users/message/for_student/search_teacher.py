import datetime

from aiogram import types
from aiogram.filters import Text, StateFilter
from aiogram.types import CallbackQuery

from keyboards.default import ForStudentsKb
from keyboards.inline.inline_keyboard import ForStudentIKb, FoundTeacherCBData
from routers.private_chat.private_chat import router
from states import ForStudentsStates
from utils.mysql import Schedule


@router.message(Text(text=ForStudentsKb.search_teacher_btn), StateFilter(ForStudentsStates.main_menu))
async def search_teacher_btn(message: types.Message, **kwargs):
    """"""
    message_text = "Щоб дізнатися \"🕵️ Де викладач?\" потрібно вибрати викладача. " \
                   "Давай спочатку виберемо першу літеру прізвища викладача"

    await message.answer(
        text=message_text,
        reply_markup=ForStudentIKb().first_letter()
    )


@router.callback_query(
    FoundTeacherCBData.filter(),
    StateFilter(ForStudentsStates.main_menu)
)
async def inline_main_menu_for_student(query: CallbackQuery, callback_data: FoundTeacherCBData):
    """вибір розкладу """
    level = callback_data.level
    type_inl_btn = callback_data.type_inl_btn
    letter = callback_data.letter
    teacher = callback_data.teacher

    levels = {
        "0": first_letter_for_teacher,
        "1": list_teacher_with_first_letter,
        "2": get_information_of_teacher,
    }

    current_level_function = levels[str(level)]

    await current_level_function(query, letter=letter, teacher=teacher)
    await query.answer(cache_time=0)


async def first_letter_for_teacher(query: CallbackQuery, **kwargs):
    message_text = "Щоб дізнатися \"🕵️ Де викладач?\" потрібно вибрати викладача. " \
                   "Давай спочатку виберемо першу літеру прізвища викладача"

    await query.message.edit_text(
        text=message_text,
        reply_markup=ForStudentIKb().first_letter()
    )


async def list_teacher_with_first_letter(query: CallbackQuery, letter: str, **kwargs):
    message_text = "Настав час обрати викладача, якого плануєш сталкерити"

    await query.message.edit_text(
        text=message_text,
        reply_markup=ForStudentIKb().list_teacher(letter=letter)
    )


async def get_information_of_teacher(query: CallbackQuery, teacher: str, **kwargs):
    day_list = ('Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця')
    number_lesson_list = ('1-2', '3-4', '5-6', '7-8', '9-10', '11-12', '13-14')

    list_information = Schedule().get_information_of_user(teacher)
    result = dict()

    for item in list_information:
        key = item.pop('day')
        len_result = len(result.get(key,[]))
        if not len_result:
            result[key]={len_result:item}
            continue
        result[key].update({len_result:item})

    message_text = f'Ймовірне розташування викладача\n«{teacher}»:\n'
    for day in day_list:
        if day not in result.keys():
            continue

        message_text+='\n<b>{day}</b>:\n'.format(day=day)
        for num_lesson in number_lesson_list:
            for key in result[day].keys():
                if not result[day][key]['number'] == num_lesson:
                    continue
                start_time = str(result[day][key]['start_time'])
                end_time = str(result[day][key]['end_time'])
                time = '{0}-{1}'.format(
                    datetime.datetime.strptime(start_time,'%H:%M:%S').strftime('%H:%M'),
                    datetime.datetime.strptime(end_time,'%H:%M:%S').strftime('%H:%M'))
                group = result[day][key]['name_group']
                lesson = result[day][key]['name']
                room = result[day][key]['room']
                message_text += '{space}{num_lesson} ({time}): \t{group} \t«{lesson}...» \t<code>{room}</code>\n'.format(
                    space=4*' ',
                    num_lesson=num_lesson, time=time, group=group, lesson=lesson[:8], room=room
                )


    await query.message.edit_text(
        text=message_text,
        reply_markup=query.message.reply_markup
    )
