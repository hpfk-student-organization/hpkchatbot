import asyncio
import datetime
from textwrap import dedent

from aiogram import types, F
from aiogram.filters import StateFilter, Command
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext

from keyboards.default import MainMenuKb, AnonymousChatKb
from routers.private_chat.private_chat import router
from states import LessonsStates, AnonymousChatStates
from utils.mysql import Replacements, AnonimChat, Holy
from utils.tools import remove_state

__state_for_command = remove_state(AnonymousChatStates.search, LessonsStates.send_my_name_group)


@router.message(
    CommandStart(),
    F.from_user.func(lambda from_user: not AnonimChat().is_check_exist_with_connect(telegram_id=from_user.id)),
    StateFilter(*__state_for_command)
)
async def commands_start_private(message: types.Message, state: FSMContext):
    AnonimChat().update_queue_status(telegram_id=message.from_user.id, status=False)
    AnonimChat().update_connect_with(telegram_id=message.from_user.id, connect_with_telegram_id=None)

    start_text = """\
    Вітаю, {first_name}.
    
    Я, бот {bot_name}, який маю багато корисної інформації для студента коледжу ХПК.
    Буду з тобою ділитися корисною інформацією і намагатися розважити.
    """
    await message.answer(
        text=dedent(start_text).format(first_name=message.from_user.first_name, bot_name="ХПФК-ашнік"),
        reply_markup=types.ReplyKeyboardRemove()
    )

    await asyncio.sleep(0.5)
    await command_main_menu(message=message, state=state)


@router.message(
    Command(commands='subscribe'),
    StateFilter(LessonsStates.main_menu)
)
async def commands_subscribe_private(message: types.Message):
    Replacements().update_subscription_status(telegram_id=message.from_user.id, status=True)
    message_text = 'Ти успішно підписався на розсилку нових замін. Якщо ти хочеш відписатися, то просто напиши ' \
                   '/unsubscribe'
    await message.answer(text=message_text)


@router.message(
    Command(commands='unsubscribe'),
    StateFilter(LessonsStates.main_menu)
)
async def commands_subscribe_private(message: types.Message):
    Replacements().update_subscription_status(telegram_id=message.from_user.id, status=False)
    message_text = 'Ти успішно відписався від розсилки на заміни. Якщо хочеш підписатися, то напиши /subscribe'
    await message.answer(text=message_text)


@router.message(
    Command(commands='hide_keyboard'),
    StateFilter(AnonymousChatStates.chat_message)
)
async def commands_hide_private(message: types.Message):
    from handlers.users.message.anonim_chat.chatting import hide_kb_in_chat
    await hide_kb_in_chat(message=message)


@router.message(
    Command(commands='show_keyboard'),
    StateFilter(AnonymousChatStates.chat_message)
)
async def commands_show_private(message: types.Message):
    message_text = "Клавіатура повернута. Щоб приховати клавіатуру - надішли команду /hide_keyboard"
    await message.answer(
        text=message_text, reply_markup=AnonymousChatKb.kb_in_chat()
    )


@router.message(
    Command(commands='setting_replacements'),
    StateFilter(*__state_for_command)
)
async def commands_edit_my_group_of_replacements(message: types.Message, state: FSMContext):
    from handlers.users.message.lessons.setting_name_group import open_menu_for_edit_name_group
    await open_menu_for_edit_name_group(message=message, state=state)


async def __remove_old_task(task: asyncio.create_task, telegram_id: int):
    if task:
        title_task = 'first_task_{0}'.format(telegram_id)
        for first_task in asyncio.all_tasks():
            if first_task.get_name() == title_task:
                first_task.cancel()
        task.set_name(title_task)
        await task


@router.message(
    Command(commands='menu'),
    StateFilter(*__state_for_command)
)
async def command_main_menu(message: types.Message, state: FSMContext):
    """ Головна функція головного меню """
    from utils.module.holy_text import get_animation
    message_text = Holy().select_text(datetime.date.today())
    task = await get_animation(message=message, message_text=message_text)
    menu_text_old = "Що ти хочеш переглянути?"
    menu_text = 'Що тебе цікавить?'
    await message.answer(
        text=menu_text,
        reply_markup=MainMenuKb.main_menu()
    )
    await state.clear()
    await __remove_old_task(task=task, telegram_id=message.from_user.id)


@router.message(
    Command(commands='menu'),
    StateFilter(*__state_for_command)
)
async def command_help(message: types.Message):
    """
    Функція інформації про бота

    @param message:
    @param state:
    @return:
    """
    message_text = "Привіт.\n" \
                   "Це неличка інформація про те, що цей бот ХПФК, має багато корисного для студентів коледжу:" \
                   " 💬 Цитати викладачів, 📄 Заміни, 🕵️ Де викладач?, і багато, багато іншого та корисного." \
                   "\n\nЗ питаннями та пропозиціями писати " \
                   "<a href='https://www.instagram.com/hpkchatbot'>сюди</a>" \
                   "\n\n<i>В тебе все вийде, потрібно тільки в себе повірити...</i>"
    await message.answer(message_text)