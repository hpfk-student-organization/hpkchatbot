from typing import Optional

from aiogram.fsm.context import FSMContext


class StorageKey:
    bot_id: int
    chat_id: int
    user_id: int
    destiny: str

    def __init__(self, bot_id: int, chat_id: int, user_id: int, destiny: str):
        self.bot_id = bot_id
        self.chat_id = chat_id
        self.user_id = user_id
        self.destiny = destiny


def FSMContextCustoms(
        state: FSMContext,
        user_id: Optional[int] = None, chat_id: Optional[int] = None,
        bot_id: Optional[int] = None, destiny: Optional[str] = None) -> FSMContext:
    """
    Install state for another user

    @param state:
    @param user_id:
    @param chat_id:
    @param bot_id:
    @param destiny:
    @return:
    """
    key = state.key
    if user_id is None:
        user_id = key.user_id

    if chat_id is None:
        chat_id = key.chat_id

    if bot_id is None:
        bot_id = key.bot_id

    if destiny is None:
        destiny = key.destiny

    return FSMContext(
        bot=state.bot,
        storage=state.storage,
        key=StorageKey(
            bot_id=bot_id, chat_id=chat_id,
            destiny=destiny, user_id=user_id,
        )

    )
