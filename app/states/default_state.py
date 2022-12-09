from aiogram.filters.state import StatesGroup as _StatesGroup, State as _State


class LessonsStates(_StatesGroup):
    main_menu = _State()
    menu_settings = _State()
    send_new_replacements = _State()
    send_my_name_group = _State()


class QuotesTeacherStates(_StatesGroup):
    main_menu = _State()
    view_quotes = _State()  # використовується тоді, коли користувач переглядає цитати
    select_teacher = _State()
    add_new_quotes = _State()
    send_quotes = _State()


class AnonymousChatStates(_StatesGroup):
    main_menu = _State()
    search = _State()
    settings = _State()
    chat_message = _State()
    close_chat = _State()


class ForStudentsStates(_StatesGroup):
    main_menu = _State()


class ADSStates(_StatesGroup):
    main_menu = _State()
