from aiogram.filters.state import StatesGroup, State 


class LessonsStates(StatesGroup):
    main_menu = State()
    menu_settings = State()
    send_new_replacements = State()
    send_my_name_group = State()


class QuotesTeacherStates(StatesGroup):
    main_menu = State()
    view_quotes = State()  # використовується тоді, коли користувач переглядає цитати
    select_teacher = State()
    add_new_quotes = State()
    send_quotes = State()


class AnonymousChatStates(StatesGroup):
    main_menu = State()
    search = State()
    settings = State()
    chat_message = State()
    close_chat = State()


class ForStudentsStates(StatesGroup):
    main_menu = State()


class ADSStates(StatesGroup):
    main_menu = State()
