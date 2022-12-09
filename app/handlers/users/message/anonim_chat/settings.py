from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboards.default import AnonymousChatKb
from keyboards.inline.inline_keyboard import AnonimChatIKb, AnonimChatWhoAmICBData, AnonimChatISMCBData
from routers.private_chat.private_chat import router
from states import AnonymousChatStates
from utils.mysql import AnonimChat


@router.message(
    Text(text=AnonymousChatKb.settings_btn),
    StateFilter(AnonymousChatStates.main_menu)
)
async def get_inl_kb_with_setting(message: types.Message, state: FSMContext):
    """Отримуємо кнопку із налаштуваннями"""
    message_text = 'Обери, що саме хочеш змінити ⤵️'

    await message.answer(
        text=message_text,
        reply_markup=AnonymousChatKb().settings()
    )
    await state.set_state(AnonymousChatStates.settings)


@router.message(
    Text(text=AnonymousChatKb.settings_who_am_i_btn),
    StateFilter(AnonymousChatStates.settings)
)
async def get_inl_kb_with_who_i(message: types.Message, state: FSMContext):
    message_text = "Обери свою стать та свій вік. Стать співрозмовника буде вибрана протилежною до твоєї"
    sex_status = AnonimChat().get_sex_in_info_user(telegram_id=message.from_user.id)

    await message.answer(
        text=message_text,
        reply_markup=AnonimChatIKb().who_am_i(sex_status=sex_status)
    )


@router.message(
    Text(text=AnonymousChatKb.it_is_me_btn),
    StateFilter(AnonymousChatStates.settings)
)
async def get_inl_kb_with_it_is_me(message: types.Message, state: FSMContext):
    message_text = "Обери, чи буде відображатися твій нікнейм в рейтингу " \
                   "користувачів в анонімному чат боті"
    show_username = AnonimChat().get_show_username_in_info_user(telegram_id=message.from_user.id)
    await message.answer(
        text=message_text,
        reply_markup=AnonimChatIKb().it_is_me(status=show_username)
    )


@router.callback_query(
    AnonimChatWhoAmICBData.filter(),
    StateFilter(AnonymousChatStates.settings)
)
async def inline_menu_setting_who_am_i(query: CallbackQuery, callback_data: AnonimChatWhoAmICBData):
    """ 🔭 Хто я? """
    type_inl_btn: str = callback_data.type_inl_btn

    AnonimChat().update_sex_in_info_user(
        telegram_id=query.from_user.id, sex=AnonimChatIKb.who_am_i_inline_callback[0] == type_inl_btn
    )

    sex_status = AnonimChat().get_sex_in_info_user(telegram_id=query.from_user.id)

    await query.message.edit_reply_markup(
        reply_markup=AnonimChatIKb().who_am_i(sex_status=sex_status)
    )
    await query.answer(cache_time=0)


@router.callback_query(
    AnonimChatISMCBData.filter(),
    StateFilter(AnonymousChatStates.settings)
)
async def inline_menu_setting_it_is_me(query: CallbackQuery, callback_data: AnonimChatISMCBData):
    """🤫 Це я"""
    type_inl_btn: str = callback_data.type_inl_btn

    AnonimChat().update_show_username_in_info_user(
        telegram_id=query.from_user.id, show_username=AnonimChatIKb.it_is_me_inline_callback[0] == type_inl_btn
    )

    status = AnonimChat().get_show_username_in_info_user(telegram_id=query.from_user.id)

    await query.message.edit_reply_markup(
        reply_markup=AnonimChatIKb().it_is_me(status=status)
    )
    await query.answer(cache_time=0)
