import asyncio

import aiogram
from aiogram import types
from aiogram.filters import Text, StateFilter
from aiogram.fsm.context import FSMContext

from keyboards.default import AnonymousChatKb
from routers.private_chat.private_chat import router
from scheduler.anonim_chat import jobs_id, add_job
from states import AnonymousChatStates
from utils.mysql import AnonimChat


@router.message(Text(text=AnonymousChatKb.start_search_btn),
                StateFilter(AnonymousChatStates.main_menu))
async def search_user_to_talk(message: types.Message, state: FSMContext, bot: aiogram.Bot):
    """При переході в розділ lesson"""
    await message.answer(
        "🔧 Чат тимчасово не доступний"
    )
    return

    if AnonimChat().get_sex_in_info_user(telegram_id=message.from_user.id) is None:
        message_text = "Щоб бот зміг з'єднати тебе з співрозмовником протилежної статі, варто спочатку вказати свою" \
                       "\n\nНа додатковій клавіатурі є кнопка «Налаштування» , скористайся нею, обравши хто ти є."
        await message.answer(
            text=message_text
        )
        return
    # if not AnonimChat().is_check_exist_in_queue(telegram_id=message.from_user.id):
    AnonimChat().update_queue_status(telegram_id=message.from_user.id, status=True)

    await state.set_state(AnonymousChatStates.search)

    sex_status_by_user = AnonimChat().get_sex_in_info_user(telegram_id=message.from_user.id)

    message_text = "Шукаємо для тебе {0} ..."
    await message.answer(
        text=message_text.format('хлопця' if not sex_status_by_user else 'дівчину'),
        reply_markup=AnonymousChatKb().search()
    )
    await add_job(bot=bot, state=state, _jobs_id=jobs_id[0])
    await asyncio.sleep(2)
    if not AnonimChat().is_check_exist_with_connect(telegram_id=message.from_user.id):
        await who_in_queue_for_search_user_to_talk(message=message)


@router.message(Text(text=AnonymousChatKb.who_online_btn, ),
                StateFilter(AnonymousChatStates.search))
async def who_in_queue_for_search_user_to_talk(message: types.Message):
    sex, count = AnonimChat().get_count_user_in_queue()

    count_in_connect = AnonimChat().get_count_with_connect()
    count_in_queue = AnonimChat().get_count_in_queue()

    count_women_in_queue = count[sex.index(0)] if sex.count(0) else 0
    count_men_in_queue = count[sex.index(1)] if sex.count(1) else 0

    message_text = "Всього в онлайн {0} людина:\n\n" \
                   "👥 Активних чатів - {1}\n\n" \
                   "В черзі - {2} 👨 та {3} 👩"
    await message.answer(
        text=message_text.format(
            count_in_connect + count_in_queue, int(count_in_connect / 2), count_men_in_queue, count_women_in_queue)
    )


@router.message(Text(text=AnonymousChatKb.cancel_search_btn),
                StateFilter(AnonymousChatStates.search))
async def cancel_search_new_user(message: types.Message, state: FSMContext):
    """Cansel find process new user for talk"""
    AnonimChat().update_queue_status(telegram_id=message.from_user.id, status=False)
    from handlers.users.message.main import anonymous_chat_button
    await anonymous_chat_button(message=message, state=state)
