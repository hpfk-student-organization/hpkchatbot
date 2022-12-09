import re

from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import ContentType

from filters.content_types import ContentTypesFilter
from keyboards.default import LessonsKb
from routers.private_chat.private_chat import router
from states import LessonsStates
from utils.mysql import Replacements


@router.message(
    Text(startswith=LessonsKb.my_group_timetable_btn),
    StateFilter(LessonsStates.menu_settings)
)
async def open_menu_for_edit_name_group(message: types.Message, state: FSMContext):
    """Переходимо в розділ із веденням групи"""
    message_text = 'Напишіть назву групи, заміни якої ти хочете отримувати'
    name_group = Replacements().get_subscription_name_group(telegram_id=message.from_user.id)
    if name_group is not None:
        message_text += '\nНа цей момент, ти відслідковуєш заміни групи {0}'.format(name_group)

    await message.answer(
        text=message_text,
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(LessonsStates.send_my_name_group)


async def __formatting_name_group(name_group: str) -> (str, bool):
    """Функція, яка перетворює в однаковий формат групи"""
    name_group = name_group.upper()
    if re.match(r'^[ІА-Я]{2,3}-[0-9]{3}[ІА-Я]?$', name_group):
        # КІБ-182 / КІБ-182З
        return name_group, True
    elif re.match(r'^[ІА-Я]{2,3}\s[0-9]{3}[ІА-Я]?$', name_group):
        # КІБ 182 / КІ-182З
        return name_group.replace(' ', '-'), True
    elif re.match(r'^[ІА-Я]{2,3}[0-9]{3}[ІА-Я]?$', name_group):
        # КІБ182 / КІБ182З
        new_group = re.findall(r'\D+|\d+\D?', name_group)
        return '{0}-{1}'.format(*new_group), True

    return name_group, False


@router.message(
    ContentTypesFilter(ContentType.TEXT),
    StateFilter(LessonsStates.send_my_name_group)
)
async def update_name_group(message: types.Message, state: FSMContext):
    """Зберігаємо назву групи"""
    new_name_group, status = await __formatting_name_group(name_group=message.text)
    message_text = 'Для більш точної подачі замін, було дещо змінену назву групи на таку: {0}'
    if not status:
        message_text = 'Не схоже що це назва групи, але я її збережу як {0}. Є шанс, що заміни можуть не надходити'
    await message.answer(text=message_text.format(new_name_group))
    Replacements().update_subscription_name_group(telegram_id=message.from_user.id, name_group=new_name_group)

    from handlers.users.message.lessons.menu_settings import get_inl_kb_with_setting
    await get_inl_kb_with_setting(message=message, state=state)
