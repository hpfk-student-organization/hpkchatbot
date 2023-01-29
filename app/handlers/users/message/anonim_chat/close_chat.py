import aiogram
from aiogram import types
from aiogram.filters import StateFilter, Text
from aiogram.fsm.context import FSMContext

from keyboards.default import AnonymousChatKb
from routers.private_chat.private_chat import router
from states import AnonymousChatStates


@router.message(Text(text=AnonymousChatKb.search_again_btn), StateFilter(AnonymousChatStates.close_chat))
async def search_again(message: types.Message, state: FSMContext, bot: aiogram.Bot):
    from handlers.users.message.anonim_chat.start_search import search_user_to_talk
    await search_user_to_talk(message=message, state=state, bot=bot)


@router.message(Text(text=AnonymousChatKb.main_menu_btn), StateFilter(AnonymousChatStates.close_chat))
async def exit_to_main_menu(message: types.Message, state: FSMContext):
    from handlers.users.message.main import anonymous_chat_button
    await anonymous_chat_button(message=message, state=state)
