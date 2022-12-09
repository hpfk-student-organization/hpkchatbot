import logging

import aiogram
from aiogram.fsm.context import FSMContext
from apscheduler.triggers.interval import IntervalTrigger

from keyboards.default import AnonymousChatKb
from settings import scheduler
from states import AnonymousChatStates
from utils.module.state import FSMContextCustoms
from utils.mysql import AnonimChat

jobs_id = ('anonim_chat',)

__MAX_INSTANCES = 1


async def create_new_anonim_chat_with_two_user(_jobs_id, bot: aiogram.Bot, state: FSMContext):
    if AnonimChat().get_if_two_sex_user_in_queue():
        logging.debug(AnonimChat().get_all_telegram_id_in_queue(sex=False))
        telegram_id_woman = list(AnonimChat().get_all_telegram_id_in_queue(sex=False))[-1]

        logging.debug(AnonimChat().get_all_telegram_id_in_queue(sex=True))
        telegram_id_man = list(AnonimChat().get_all_telegram_id_in_queue(sex=True))[0]

        AnonimChat().update_connect_with(telegram_id=telegram_id_man, connect_with_telegram_id=telegram_id_woman)
        AnonimChat().update_connect_with(telegram_id=telegram_id_woman, connect_with_telegram_id=telegram_id_man)

        AnonimChat().update_queue_status(telegram_id=telegram_id_man, status=False)
        AnonimChat().update_queue_status(telegram_id=telegram_id_woman, status=False)

        message_text = "Вас з'єднано!"
        for telegram_id in (telegram_id_man, telegram_id_woman):
            await bot.send_message(
                chat_id=telegram_id,
                text=message_text,
                reply_markup=AnonymousChatKb.kb_in_chat()
            )
            state_new = FSMContextCustoms(state=state, user_id=telegram_id, chat_id=telegram_id)
            await state_new.set_state(AnonymousChatStates.chat_message)
        return

    scheduler.remove_job(_jobs_id)


async def add_job(bot: aiogram.Bot, state: FSMContext, _jobs_id):
    scheduler.add_job(
        func=create_new_anonim_chat_with_two_user,
        args=[_jobs_id, bot, state],
        trigger=IntervalTrigger(),
        max_instances=__MAX_INSTANCES,
        id=_jobs_id
    )
