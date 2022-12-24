from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default import LessonsKb
from keyboards.inline.inline_keyboard import ScheduleIKb, ScheduleMMCBData, ScheduleMyGroupCBData, \
    ScheduleAnotherGroupCBData
from routers.private_chat.private_chat import router
from states import LessonsStates
from utils.module.message_tool import ErrorEntryData
from utils.mysql import Replacements, Schedule


@router.message(
    Text(text=LessonsKb.timetable_btn),
    StateFilter(LessonsStates.main_menu)
)
async def get_inl_kb_with_schedule(message: types.Message, state: FSMContext):
    """Отримаємо клавіатуру з розкладом"""
    message_text = "Виберіть, розклад якої групи ви хочете переглянути:"
    name_group = Replacements().get_subscription_name_group(telegram_id=message.from_user.id)
    await message.answer(
        text=message_text,
        reply_markup=ScheduleIKb(name_group).main_btn(),
    )


@router.callback_query(
    ScheduleMMCBData.filter(),
    StateFilter(LessonsStates.main_menu)
)
async def inline_main_menu_schedule(query: CallbackQuery, callback_data: ScheduleMMCBData):
    """вибір розкладу """
    name_group = callback_data.my_group
    type_inl_btn = callback_data.type_inl_btn

    if ScheduleIKb.main_btn_inline_callback[0] == type_inl_btn:
        "Якщо кнопка - Моя група"
        if name_group is None:
            raise ErrorEntryData('Група не вказана')
        await select_my_group_btn(query=query, name_group=name_group)

    elif ScheduleIKb.main_btn_inline_callback[1] == type_inl_btn:
        "Якщо кнопка - Інші групи"
        await select_another_group_btn(query=query, name_group=name_group)


#
#   Секція - Моя група
#

async def select_my_group_btn(query: CallbackQuery, name_group: str):
    """Коли натиснули кнопку з групою"""
    await query.message.edit_reply_markup(
        reply_markup=ScheduleIKb(name_group).my_selected_group(),
    )


@router.callback_query(
    ScheduleMyGroupCBData.filter(),
    StateFilter(LessonsStates.main_menu)
)
async def inline_my_group_select_day(query: CallbackQuery, callback_data: ScheduleMyGroupCBData):
    """ Показ розкладу для моєї групи """
    my_group = callback_data.my_group
    weekday = callback_data.weekday
    num_s = callback_data.num_s



    reply_markup = ScheduleIKb(name_group=my_group).my_selected_group(
        select_weekday=weekday, click_num_s=num_s)

    message_text = select_day_schedule(day=int(weekday), name_group=my_group, num_s=num_s)

    await query.message.edit_text(
        text=message_text,
        reply_markup=reply_markup
    )


def select_day_schedule(day: int, name_group: str, num_s: bool = True) -> str:
    """
    Збирає розклад, для вказаного дня

    @return: Готовий розклад на вибраний день
    """

    day_list = ('Понеділок', 'Вівторок', 'Середа', 'Четвер', 'П\'ятниця')
    number_lesson_list = ('1-2', '3-4', '5-6', '7-8', '9-10', '11-12', '13-14')
    error_message = 'Розклад тимчасово не доступний'

    type_date = 'Чисельник' if num_s else 'Знаменник'
    title_day = day_list[day]


    structure_message = '{name_group} - {day}({type_week}):\n\n'
    structure_message+= ''
    return '{0},{1},{2}'.format(name_group, day, num_s)


#
#   Секція - Інші групи
#


@router.callback_query(
    ScheduleAnotherGroupCBData.filter(),
    StateFilter(LessonsStates.main_menu)
)
async def inline_my_group_select_day(query: CallbackQuery, callback_data: ScheduleAnotherGroupCBData):
    """ Показ розкладу для інших груп """
    my_group = callback_data.my_group
    weekday = callback_data.weekday
    num_s = callback_data.num_s
    select_my_g = callback_data.select_my_g

    all_group = Schedule().get_all_title_group_u()

    if not all_group:
        raise ErrorEntryData('2')

    if weekday is not None:
        reply_markup = ScheduleIKb(name_group=my_group).another_group(
            select_name_group=select_my_g,
            select_weekday=weekday, click_num_s=num_s, all_group=all_group)
        message_text = select_day_schedule(day=int(weekday), name_group=select_my_g, num_s=num_s)
    else:
        message_text = "Виберіть, розклад якої групи ви хочете переглянути:"
        reply_markup = ScheduleIKb(name_group=my_group).another_group(
            select_name_group=select_my_g,
            select_weekday=weekday, all_group=all_group)

    await query.message.edit_text(
        text=message_text,
        reply_markup=reply_markup
    )


async def select_another_group_btn(query: CallbackQuery, name_group: str):
    """Коли натиснули кнопка - Інші групи"""
    all_group = Schedule().get_all_title_group_u()
    if not all_group:
        raise ErrorEntryData('Список груп, тим часово не доступний. Спробуйте пізніше.')
    reply_markup = ScheduleIKb(name_group).another_group(all_group=all_group)
    await query.message.edit_reply_markup(
        reply_markup=reply_markup
    )
