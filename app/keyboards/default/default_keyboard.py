from typing import Optional

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from utils.module.keyboard import zip_adjust, zip_builder
from utils.mysql import QuotesTeacher


def _reply_keyboard_builder(text_btn_args: Optional[tuple | list],
                            adjust: Optional[tuple] = None) -> ReplyKeyboardMarkup | ReplyKeyboardBuilder:
    """basic builder"""
    return zip_builder(
        text_btn_args=text_btn_args,
        builder=ReplyKeyboardBuilder(),
        adjust=adjust
    )


class BaseButton:
    back_btn = '🏠 Назад'
    settings_btn = '⚙️ Налаштування'
    send_btn = '🏠 Надіслати'

    @staticmethod
    def _back() -> ReplyKeyboardMarkup:
        """Клавіатура back"""
        _ = BaseButton

        tuple_btn = _.back_btn,

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)


class MainMenuKb:
    """Відповідає за головне меню, яке з'являється в особистих повідомленнях бота"""

    lessons_btn = '📖 Пари'
    for_students_btn = '🧑‍🎓 Студентам'
    anonymous_chat_btn = '💬 Анонімний чат'
    ads_btn = '📋 Оголошення'
    quotes_btn = '💬 Цитати викладачів'

    menu_btn = '📜 Меню'
    good_btn = '👌 Зрозуміло'

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        _ = MainMenuKb

        tuple_btn = _.lessons_btn, _.for_students_btn, _.ads_btn, _.anonymous_chat_btn, _.quotes_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(2)
        ).as_markup(resize_keyboard=True)


class LessonsKb(BaseButton):
    """Меню 2-го рівня Пари"""
    replacements_btn = '📄 Заміни'
    timetable_btn = '📗 Розклад'
    hours_lessons_btn = '🕓 Години занять'

    send_new_replacements_btn = '➕ Надіслати нові заміни'
    send_anonim_replacements_btn = 'Відправити анонімно'
    send_replacements_with_username_btn = 'Відправити з посиланням на себе'

    how_get_replacements_btn = '🗞 Як отримувати заміни?'
    my_group_timetable_btn = '👥 Моя група'

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        _ = LessonsKb

        tuple_btn = _.replacements_btn, _.timetable_btn, _.hours_lessons_btn, _.settings_btn, _.send_new_replacements_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(2, 2, 1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def settings(name_group: Optional[str]) -> ReplyKeyboardMarkup:
        _ = LessonsKb

        tuple_btn = _.how_get_replacements_btn, '{0} {1}'.format(_.my_group_timetable_btn, name_group), _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(2, 1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def back() -> ReplyKeyboardMarkup:
        return QuotesTeacherKb._back()

    @staticmethod
    def send_replacements() -> ReplyKeyboardMarkup:
        _ = LessonsKb

        tuple_btn = _.send_anonim_replacements_btn, _.send_replacements_with_username_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)


class ForStudentsKb(BaseButton):
    """Меню 2-го рівня Для студентів"""

    search_teacher_btn = '🕵️ Де викладач?'

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        _ = ForStudentsKb

        tuple_btn = _.search_teacher_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)


class QuotesTeacherKb(BaseButton):
    """Меню 2-го рівня Цитати викладачів"""

    send_quotes_btn = '➕ Додати нову цитату'
    next_btn = '▶'
    last_btn = '◀'
    repeat_btn = '💬 Ще одна'

    @staticmethod
    def __convert_amount_list_btn_to_tuple(len_tuple_btn: Optional[int]) -> tuple:
        amount_btn_in_structure_tuple = *(1 + bool(len_tuple_btn - 1),) * (
                len_tuple_btn // 2 + 0 ** (len_tuple_btn - 1)
        ), len_tuple_btn % 2 - 0 ** (len_tuple_btn - 1)

        return amount_btn_in_structure_tuple

    @staticmethod
    def main_menu(
            list_all_teachers: Optional[list],
            number_page: Optional[int] = 1,
            amount_teacher_btn_on_page: Optional[int] = 4) -> ReplyKeyboardMarkup:
        """
            Keyboard for page with quotes

        Args:
            list_all_teachers:
            amount_teacher_btn_on_page: the number of btn with teachers that will be displayed in the menu with the
            choice of teacher
            number_page: the number page in quotes

        Returns: Keyboard with button teacher

        """

        _ = QuotesTeacherKb

        first_index = 0 + amount_teacher_btn_on_page * (number_page - 1)  # формула обрахунку індексу по лівій межі
        last_index = amount_teacher_btn_on_page - 1 + amount_teacher_btn_on_page * (number_page - 1)  # по правій межі

        teacher_btn = [list_all_teachers[index_item] for index_item in range(len(list_all_teachers)) if
                       first_index <= index_item <= last_index]  # визначимо кнопки, якій попадають під вказану межу

        # get emoji of teacher
        teacher_with_emoji_btn = [
            _teacher_text if _emoji is None else '{0} {1}'.format(_emoji, _teacher_text)
            for _teacher_text, _emoji in QuotesTeacher().select_emoji_of_teacher(list_teachers=teacher_btn)
        ]

        # зберемо до купи всі кнопки
        tuple_zip_btn = *teacher_with_emoji_btn, _.send_quotes_btn, _.last_btn, _.back_btn, _.next_btn

        return _reply_keyboard_builder(  # доробити формулу, щоб воно працювало при будь-яких розмірах
            tuple_zip_btn, adjust=zip_adjust(
                *_.__convert_amount_list_btn_to_tuple(len(teacher_btn)),
                1, 3)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def quotes() -> ReplyKeyboardMarkup:
        """Коли ми переглядаємо цитати викладача"""
        _ = QuotesTeacherKb

        tuple_btn = _.repeat_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def back() -> ReplyKeyboardMarkup:
        return QuotesTeacherKb._back()

    @staticmethod
    def send_quotes() -> ReplyKeyboardMarkup:
        """Коли надсилаємо цитату"""
        _ = QuotesTeacherKb

        tuple_btn = _.send_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1, repeat=True)
        ).as_markup(resize_keyboard=True)


class AnonymousChatKb(BaseButton):
    """Меню 2-го рівня Анонімний чат"""
    start_search_btn = '🔍 Почати пошук'
    ranked_btn = '⭐ Рейтинг'
    settings_who_am_i_btn = '🔭 Хто я?'
    it_is_me_btn = '🤫 Це я'

    who_online_btn = '🌐 Хто онлайн?'
    cancel_search_btn = '🚫 Скасувати пошук'

    leave_chat_btn = '🚫 Завершити чат'
    hide_keyboard_btn = '⌨️ Сховати меню'

    exit_chat_btn = '🚪 Завершити та вийти'
    back_in_chat_btn = '🙃 Ні, я передумав'

    search_again_btn = '🔍 Шукати знову'
    main_menu_btn = '🏠 Повернутися до головного меню'

    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        _ = AnonymousChatKb

        tuple_btn = _.start_search_btn, _.ranked_btn, _.settings_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(2, 1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def settings() -> ReplyKeyboardMarkup:
        _ = AnonymousChatKb

        tuple_btn = _.settings_who_am_i_btn, _.it_is_me_btn, _.back_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(2, 1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def search() -> ReplyKeyboardMarkup:
        _ = AnonymousChatKb

        tuple_btn = _.who_online_btn, _.cancel_search_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def kb_in_chat() -> ReplyKeyboardMarkup:
        """З'являється при спілкуванні з 2-х співрозмовників між собою"""
        _ = AnonymousChatKb

        tuple_btn = _.leave_chat_btn, _.hide_keyboard_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def exit_chat() -> ReplyKeyboardMarkup:
        """Запитує чи користувач хоче покинути чат"""
        _ = AnonymousChatKb

        tuple_btn = _.exit_chat_btn, _.back_in_chat_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def search_or_exit_in_menu() -> ReplyKeyboardMarkup:
        """Запитує чи потрібно шукати співрозмовника чи покинути чат"""
        _ = AnonymousChatKb

        tuple_btn = _.search_again_btn, _.main_menu_btn

        return _reply_keyboard_builder(
            tuple_btn, adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)
