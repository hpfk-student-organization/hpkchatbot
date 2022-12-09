from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext

from keyboards.default import LessonsKb
from routers.private_chat.private_chat import router
from states import LessonsStates
from utils.mysql import Replacements


@router.message(
    Text(text=LessonsKb.settings_btn),
    StateFilter(LessonsStates.main_menu)
)
async def get_inl_kb_with_setting(message: types.Message, state: FSMContext):
    """Отримуємо кнопку із налаштуваннями"""
    message_text = 'Виберіть, що саме ви плануєте налаштувати:'
    name_group = Replacements().get_subscription_name_group(telegram_id=message.from_user.id)
    await message.answer(
        text=message_text,
        reply_markup=LessonsKb.settings(name_group='- невказана' if name_group is None else name_group)
    )
    await state.set_state(LessonsStates.menu_settings)

