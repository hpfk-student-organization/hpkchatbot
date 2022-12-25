from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext

from keyboards.default import AnonymousChatKb
from routers.private_chat.private_chat import router
from states import AnonymousChatStates
from utils.mysql import AnonimChat


@router.message(
    Text(text=AnonymousChatKb.ranked_btn),
    StateFilter(AnonymousChatStates.main_menu)
)
async def get_inl_kb_with_setting(message: types.Message, state: FSMContext):
    """Отримуємо кнопку із налаштуваннями"""
    message_text = "Рейтинг найактивніших користувачів в анонімному чат боті\n" \
                   "Очки рейтинга отримуються за допомогою активності в боті 😎 {0}"

    information_of_users = AnonimChat().get_all_info_for_top_rating_users()
    if information_of_users:
        keys, info_user_list = information_of_users
        table_rating = ''
        template = '{0} місце - {1} - {2} повідомлень\n'
        number = 0
        for user in info_user_list:
            number += 1
            username, count_message, show_username = user
            if show_username and not username is None:
                table_rating += template.format(number, '@' + username, count_message)
                continue
            table_rating += template.format(number, '🤫', count_message)

        await message.answer(text=message_text.format('\n\n' + table_rating))
        return

    await message.answer(text=message_text.format('\n\nНа даний момент, тут нікого немає'))
