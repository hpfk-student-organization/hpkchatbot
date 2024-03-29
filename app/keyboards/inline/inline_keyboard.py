import math
from typing import Optional, List

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from memoization import cached

from keyboards.inline.base import BaseButton, _inline_builder
from utils.module.keyboard import zip_adjust
from utils.module.language import UA_RUS_EN
from utils.mysql import QuotesTeacher, Schedule

TTL_CACHE = 12 * 60 * 60


class SendNewQuotesCBData(CallbackData, prefix='SendNQts'):
    """Клас з Callback-ми для клавіатури з відправленням нової цитати"""
    level: int = 0  # відповідає за рівень
    first_letter: str = None
    teacher: str = None


class VerificationQuotesCBData(CallbackData, prefix='VerifQst'):
    """Клас з Callback-ми для перевірки нової цитати"""
    level: int = 0  # відповідає за рівень
    type_inl_btn: str  # тип кнопки, яку ми натискаємо
    user_id: int  # Telegram id user. Потрібен для того, щоб знати, хто надіслав цитату
    message_id: int = None  # message id повідомлення. Щоб можна було прикріпити reply з відповіддю
    message_id_send_btn: int = None  # message_id кнопки, яку натискає користувач, щоб відправити цитату


class VerificationReplacementsCBData(VerificationQuotesCBData, CallbackData, prefix='VerifPhoto'):
    show_information_user: bool = False


class AnonimChatISMCBData(CallbackData, prefix='it_is_me'):
    level: int = 0  # відповідає за рівень
    type_inl_btn: str  # тип кнопки, яку ми натискаємо


class AnonimChatWhoAmICBData(AnonimChatISMCBData, CallbackData, prefix='who_am_i'):
    pass


class ScheduleMMCBData(AnonimChatISMCBData, CallbackData, prefix='main_menu'):
    my_group: str = None


class ScheduleMyGroupCBData(ScheduleMMCBData, CallbackData, prefix='my_g'):
    weekday: str = None  # день тижня
    num_s: bool = None  # чисельник чи знаменник


class ScheduleAnotherGroupCBData(ScheduleMyGroupCBData, CallbackData, prefix='another_g'):
    select_my_g: str = ''


class LessonsCBData(CallbackData, prefix='Lesson'):
    level: int = 0  # відповідає за рівень
    type_inl_btn: str  # тип кнопки, яку ми натискаємо
    callback_id: int = 0  # ID кнопки, яку ми натиснули
    message_id: str = None


class FoundTeacherCBData(CallbackData, prefix='f_teacher'):
    level: int = 0
    type_inl_btn: str  # тип кнопки, яку ми натискаємо
    letter: str = None
    teacher: str = None


class SendNewQuotesIKb(BaseButton):
    like_inl_btn = '👍'
    dislike_inl_btn = '👎'

    def quotes(self) -> InlineKeyboardMarkup:
        tuple_btn = self.like_inl_btn, self.dislike_inl_btn
        tuple_callback_data_btn = SendNewQuotesCBData(level=1), SendNewQuotesCBData(level=1)

        return _inline_builder(
            text_btn_args=tuple_btn,
            callback_data_btn_args=tuple_callback_data_btn,
            adjust=zip_adjust(2, repeat=True)
        ).as_markup(resize_keyboard=True)

    def first_letter_with_all_teacher_in_send_new_quotes(self):
        """Клавіатура з літер"""
        CURRENT_LEVEL = 0
        first_letters: list = QuotesTeacher().get_first_letter_with_all_teacher()

        callback_data_list: list = [
            SendNewQuotesCBData(level=CURRENT_LEVEL + 1, first_letter=first_letter) for first_letter in
            first_letters]

        return _inline_builder(
            text_btn_args=first_letters,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(6, repeat=True)
            # adjust=zip_adjust(math.floor(math.sqrt(len(first_letters))), repeat=True)
        ).as_markup(resize_keyboard=True)

    def all_teacher_in_letter_send_new_quotes(self, first_letter: Optional[str], view_mode: Optional[int] = 1):
        """Клавіатура з викладачами відфільтрована по першій літері"""
        CURRENT_LEVEL = 1
        list_teacher: list = QuotesTeacher().get_all_teacher_with_first_letter(first_letter=first_letter)

        callback_data_list: list = [
            SendNewQuotesCBData(level=CURRENT_LEVEL + 1, teacher=teacher) for teacher in list_teacher]

        _builder = _inline_builder(
            text_btn_args=list_teacher,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(int(math.sqrt(len(list_teacher) + view_mode)), repeat=True)
            # adjust=zip_adjust(int(math.sqrt(len(list_teacher))), repeat=True)
        )

        return _inline_builder(
            text_btn_args=(self.back_btn,),
            callback_data_btn_args=(SendNewQuotesCBData(level=CURRENT_LEVEL - 1),),
            builder=_builder,
            method_create='row'
        ).as_markup(resize_keyboard=True)


class VerificationQuotesIKb(BaseButton):
    verification_inline_callback: tuple = ('correct_and_save', 'incorrect', 'correct')
    verification_inl_btn: dict = {
        verification_inline_callback[0]: '💾 Зберегти цитату',
        verification_inline_callback[1]: '❌ Не зберігати',
        verification_inline_callback[2]: '✔ Цитата правильна'
    }

    feedback_inline_callback: tuple = ('send_feedback', 'back_inl_btn')
    feedback_inl_bnt: dict = {
        feedback_inline_callback[0]: 'Надіслати відгук',
        feedback_inline_callback[1]: 'Назад'
    }

    def verification(self, user_id: Optional[int], message_id_send_btn: Optional[int]):
        """Клавіатура перевіркою цитати"""
        CURRENT_LEVEL = 0
        text_btn = tuple(self.verification_inl_btn.values())

        callback_data_list: list = [
            VerificationQuotesCBData(
                level=CURRENT_LEVEL + 1, type_inl_btn=type_btn, user_id=user_id, message_id_send_btn=message_id_send_btn
            )
            for type_btn in self.verification_inl_btn.keys()
        ]

        return _inline_builder(
            text_btn_args=text_btn,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(2)

        ).as_markup(resize_keyboard=True)

    def send_feed_back(self, user_id: Optional[int], message_id: Optional[int]):
        """Клавіатура перевіркою цитати"""
        CURRENT_LEVEL = 1

        callback_data_list: tuple = (
            VerificationQuotesCBData(
                level=CURRENT_LEVEL + 1,
                type_inl_btn=self.feedback_inline_callback[0],
                user_id=user_id,
                message_id=message_id,
            ),
        )

        return _inline_builder(
            text_btn_args=(self.feedback_inl_bnt['send_feedback'],),
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)

    def back(self, user_id: Optional[int], message_id: Optional[int]):
        """Клавіатура перевіркою цитати"""
        CURRENT_LEVEL = 2

        callback_data_list: tuple = (
            VerificationQuotesCBData(
                level=CURRENT_LEVEL - 1,
                type_inl_btn=self.feedback_inline_callback[1],
                user_id=user_id,
                message_id=message_id,
            ),
        )

        return _inline_builder(
            text_btn_args=(self.feedback_inl_bnt['back_inl_btn'],),
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)


class LessonsIKb:
    get_replacements_inline_callback: tuple = ('see_with_site', 'see_photo')
    get_replacements_inl_bnt: dict = {
        get_replacements_inline_callback[0]: '🌐 Показати з сайту',
        get_replacements_inline_callback[1]: '📷 Показати фото'
    }

    # status_replacements_inline_callback: tuple = ('off_send', 'on_send')
    # send_method_replacements_inline_callback: tuple = ('only_photo', 'only_text', 'all', 'only_first')
    type_replacements_inline_callback = ('status', 'send_method')
    status_replacements_list_inl_btn: list = ['🔔 Ввімкнути', '🔕 Вимкнути']
    send_method_replacements_list_inl_btn: list = ['📷 Лише фото', '🌐 Лише з сайту', '📮 Те і те', '⏳ Щось перше']

    def get_replacements(self, message_id: Optional[str], inline_callback_text: Optional[str] = None):
        """
            Inline keyboard with ...

        Args:
            message_id:
            inline_callback_text:

        Returns:
            Note

        """

        if inline_callback_text is None:
            inline_callback_text = self.get_replacements_inline_callback[-1]

        type_inl_btn = self.get_replacements_inline_callback[
            1 - self.get_replacements_inline_callback.index(inline_callback_text)]
        callback_data_list: tuple = (
            LessonsCBData(
                type_inl_btn=type_inl_btn,
                message_id=message_id
            ),
        )

        return _inline_builder(
            text_btn_args=(self.get_replacements_inl_bnt[type_inl_btn],),
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)

    def setting_send_replacements(self, status: Optional[bool | int], send_method=Optional[int]):
        """

        Args:
            status: True/False - 1 or 0
            send_method: 1 or 2 or 3 or 4

        Returns:

        """
        select_text = '➡️ {} ⬅️'

        status_replacements_list_inl_btn = self.status_replacements_list_inl_btn.copy()
        status_replacements_list_inl_btn[1 - int(status)] = select_text.format(
            status_replacements_list_inl_btn[1 - int(status)]
        )

        send_method_replacements_list_inl_btn = self.send_method_replacements_list_inl_btn.copy()
        send_method_replacements_list_inl_btn[send_method - 1] = select_text.format(
            send_method_replacements_list_inl_btn[send_method - 1]
        )
        callback_data_list: list = [LessonsCBData(
            type_inl_btn=self.type_replacements_inline_callback[0],
            callback_id=id_btn
        ) for id_btn in range(len(status_replacements_list_inl_btn) - 1, -1, -1)] + [LessonsCBData(
            type_inl_btn=self.type_replacements_inline_callback[1],
            callback_id=id_btn + 1
        ) for id_btn in range(len(send_method_replacements_list_inl_btn))]

        return _inline_builder(
            text_btn_args=status_replacements_list_inl_btn + send_method_replacements_list_inl_btn,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(2, 1)
        ).as_markup(resize_keyboard=True)


class VerificationReplacementsIKb(VerificationQuotesIKb, BaseButton):
    verification_inline_callback: tuple = ('send_and_save', 'save', 'incorrect')
    verification_inl_btn: dict = {
        verification_inline_callback[0]: '✉ Розіслати та зберегти',
        verification_inline_callback[1]: '💾 Зберегти',
        verification_inline_callback[2]: '❌ Не зберігати'
    }

    feedback_inline_callback: tuple = ('send_feedback', 'back_inl_btn')
    feedback_inl_bnt: dict = {
        feedback_inline_callback[0]: 'Надіслати відгук',
        feedback_inline_callback[1]: 'Назад'
    }

    def verification(self, user_id: Optional[int], message_id_send_btn: Optional[int],
                     show_information_user: Optional[bool] = False):
        """Клавіатура перевіркою цитати"""
        CURRENT_LEVEL = 0
        text_btn = tuple(self.verification_inl_btn.values())

        callback_data_list: list = [
            VerificationReplacementsCBData(
                level=CURRENT_LEVEL + 1, type_inl_btn=type_btn, user_id=user_id,
                show_information_user=show_information_user,
                message_id_send_btn=message_id_send_btn

            )
            for type_btn in self.verification_inl_btn.keys()
        ]

        return _inline_builder(
            text_btn_args=text_btn,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(2)

        ).as_markup(resize_keyboard=True)

    def send_feed_back(self, user_id: Optional[int], message_id: Optional[int]):
        """Клавіатура перевіркою цитати"""
        CURRENT_LEVEL = 1

        callback_data_list: tuple = (
            VerificationReplacementsCBData(
                level=CURRENT_LEVEL + 1,
                type_inl_btn=self.feedback_inline_callback[0],
                user_id=user_id,
                message_id=message_id,
            ),
        )

        return _inline_builder(
            text_btn_args=(self.feedback_inl_bnt['send_feedback'],),
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)

    def back(self, user_id: Optional[int], message_id: Optional[int]):
        """Клавіатура перевіркою цитати"""
        CURRENT_LEVEL = 2

        callback_data_list: tuple = (
            VerificationReplacementsCBData(
                level=CURRENT_LEVEL - 1,
                type_inl_btn=self.feedback_inline_callback[1],
                user_id=user_id,
                message_id=message_id,
            ),
        )

        return _inline_builder(
            text_btn_args=(self.feedback_inl_bnt['back_inl_btn'],),
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)


class AnonimChatIKb(BaseButton):
    who_am_i_inline_callback: tuple = ('boy', 'girl')
    who_am_i_inl_btn: dict = {
        who_am_i_inline_callback[0]: '👨 Хлопець',
        who_am_i_inline_callback[1]: '👩 Дівчина',
    }

    it_is_me_inline_callback: tuple = ('show', 'hide')
    it_is_me_inl_bnt: dict = {
        it_is_me_inline_callback[0]: 'Показати',
        it_is_me_inline_callback[1]: 'Приховати'
    }

    def it_is_me(self, status: Optional[bool]):
        select_text = '➡️ {} ⬅️'

        text_btn_list = list(self.it_is_me_inl_bnt.values())
        text_btn_list[1 - int(status)] = select_text.format(
            text_btn_list[1 - int(status)]
        )

        callback_data_list = [
            AnonimChatISMCBData(
                type_inl_btn=types,
            ) for types in self.it_is_me_inline_callback
        ]

        return _inline_builder(
            text_btn_args=text_btn_list,
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)

    def who_am_i(self, sex_status: Optional[bool | int] = None):
        select_text = '➡️ {} ⬅️'
        # доробити підтримку None
        text_btn_list = list(self.who_am_i_inl_btn.values())
        if not sex_status is None:
            text_btn_list[1 - int(sex_status)] = select_text.format(
                text_btn_list[1 - int(sex_status)]
            )

        callback_data_list = [
            AnonimChatWhoAmICBData(
                type_inl_btn=types,
            ) for types in self.who_am_i_inline_callback
        ]

        return _inline_builder(
            text_btn_args=text_btn_list,
            callback_data_btn_args=callback_data_list,
        ).as_markup(resize_keyboard=True)


class ScheduleIKb(BaseButton):
    main_btn_inline_callback: tuple = ('my_group', 'another_group')
    main_btn_inl_btn: dict = {
        main_btn_inline_callback[0]: 'Моя група',
        main_btn_inline_callback[1]: 'Інші групи',
    }

    day_my_group_inl_btn: tuple = ('Пн.', 'Вт.', 'Ср.', 'Чт.', 'Пт.')
    day_my_group_inline_callback: list = list(map(str, range(len(day_my_group_inl_btn))))
    numerator_inl_btn = ('Знаменник', 'Чисельник')
    numerator_inline_callback = (False, True)

    day_my_group_type_inline_callback = ('weekday', 'num_s')

    def __init__(self, name_group: str):
        self.name_group = name_group

        basic_text_btn: list = list(self.main_btn_inl_btn.values())
        basic_text_btn[0] = '{0} {1}'.format(
            basic_text_btn[0], '- невказана' if name_group is None else name_group)

        self.basic_text_btn = basic_text_btn
        self.callback_data_list = [ScheduleMMCBData(
            type_inl_btn=types, my_group=name_group) for types in self.main_btn_inline_callback]

    def main_btn(self):
        """
        Головна клавіатура

        @return:
        """
        return _inline_builder(
            text_btn_args=self.basic_text_btn,
            callback_data_btn_args=self.callback_data_list,
            adjust=zip_adjust(1)
        ).as_markup(resize_keyboard=True)

    @staticmethod
    def __select_btn(btn: str, l_prefix='👉 ', r_prefix=' 👈') -> str:
        title_text = l_prefix + '{}' + r_prefix
        return title_text.format(btn)

    def __create_callback_my_group(self, type_inl_btn, weekday, num_s) -> ScheduleMyGroupCBData:
        return ScheduleMyGroupCBData(
            my_group=self.name_group,
            type_inl_btn=type_inl_btn,
            weekday=weekday,
            num_s=num_s
        )

    def __select_weekday_btn_for_my_group(
            self, text_btn_list: list, click_num_s: bool, name_group: str, select_weekday: str,
            callback_data_list: List[ScheduleMyGroupCBData],
            adjust: list
    ) -> (List[str], List[ScheduleMyGroupCBData], list):
        """Генерує кнопки з вибором дня"""
        text_btn_list = [self.numerator_inl_btn[int(not click_num_s)], *text_btn_list]

        callback_data = self.__create_callback_my_group(
            self.day_my_group_type_inline_callback[0], select_weekday, not click_num_s
        )
        callback_data_list = [callback_data, *callback_data_list]

        adjust = zip_adjust(1, *adjust)

        return text_btn_list, callback_data_list, adjust

    def my_selected_group(self, select_weekday: str = None, click_num_s: bool = True):
        """
        Коли користувач вибрав групу або день розкладу

        @return:
        """
        name_group = self.name_group
        basic_text_btn = self.basic_text_btn
        basic_callback_data_list = self.callback_data_list

        # збираємо базову структуру кнопок, до моменту вибору дня
        text_btn_list = [
            self.__select_btn(basic_text_btn[0]), *self.day_my_group_inl_btn, basic_text_btn[-1]
        ]

        callback_data_list = [
            self.__create_callback_my_group(
                self.day_my_group_type_inline_callback[0], weekday, click_num_s)
            for weekday in self.day_my_group_inline_callback
        ]
        callback_data_list = [basic_callback_data_list[0], *callback_data_list, basic_callback_data_list[-1]]

        adjust = zip_adjust(1, 5, 1)

        if select_weekday is not None:
            text_btn_list, callback_data_list, adjust = self.__select_weekday_btn_for_my_group(
                text_btn_list=text_btn_list,
                click_num_s=click_num_s, name_group=name_group, select_weekday=select_weekday,
                callback_data_list=callback_data_list,
                adjust=adjust
            )

        return _inline_builder(
            text_btn_args=text_btn_list,
            callback_data_btn_args=callback_data_list,
            adjust=adjust
        ).as_markup(resize_keyboard=True)

    def __create_callback_another_group(
            self, type_inl_btn, select_my_g, weekday=None, num_s=None,
    ) -> ScheduleAnotherGroupCBData:
        return ScheduleAnotherGroupCBData(
            my_group=self.name_group,
            type_inl_btn=type_inl_btn,
            select_my_g=select_my_g,
            weekday=weekday,
            num_s=num_s,

        )

    def __create_kb_with_select_group(
            self, text_btn_list, callback_data_list, adjust,
            select_name_group, type_inl_btn, click_num_s, select_weekday
    ) -> (List[str], List[ScheduleMyGroupCBData], list):
        # розділяємо категорії btn на дві групи: базові кнопки, та кнопки із назвами груп
        basic_btn, another_btn = text_btn_list[:2], text_btn_list[2:]
        basic_callback_btn, another_callback_btn = callback_data_list[:2], callback_data_list[2:]

        pos_btn = another_btn.index(select_name_group)  # отримуємо позицію кнопки
        line_pos_btn = pos_btn // 5  # на якій лінії, кнопка
        add_btn = 6 - pos_btn % 5  # скільки кнопок потрібно додати, щоб опинитися на наступному рядку

        text_btn_list = [
            *basic_btn,
            *another_btn[:pos_btn],
            *another_btn[pos_btn + 1:pos_btn + add_btn],
            select_name_group,
            *self.day_my_group_inl_btn,
            *another_btn[pos_btn + add_btn:]
        ]

        # Генеруємо callback для кнопок
        select_group_callback_data = self.__create_callback_another_group(
            type_inl_btn=type_inl_btn, select_my_g=select_name_group
        )
        day_callback_data_list = [self.__create_callback_another_group(
            type_inl_btn=type_inl_btn, select_my_g=select_name_group, weekday=weekday, num_s=click_num_s
        ) for weekday in self.day_my_group_inline_callback]

        callback_data_list = [
            *basic_callback_btn,
            *another_callback_btn[:pos_btn],
            *another_callback_btn[pos_btn + 1:pos_btn + add_btn],
            select_group_callback_data,
            *day_callback_data_list,
            *another_callback_btn[pos_btn + add_btn:]
        ]
        adjust = zip_adjust(1, 1, *(5,) * (line_pos_btn + 1), 1, 5)

        if select_weekday is not None:
            type_week_text_btn = self.numerator_inl_btn[int(not click_num_s)]
            type_week_callback_data = self.__create_callback_another_group(
                type_inl_btn=self.day_my_group_type_inline_callback[0],
                weekday=select_weekday, num_s=not click_num_s, select_my_g=select_name_group
            )
            text_btn_list = [type_week_text_btn, *text_btn_list]
            callback_data_list = [type_week_callback_data, *callback_data_list]
            adjust = (1, *adjust)

        return text_btn_list, callback_data_list, adjust

    def another_group(
            self, all_group: tuple | list,
            select_name_group: str = None, select_weekday: str = None, click_num_s: bool = True):
        """
        Клавіатура з усіма групами та вибраною групою

        @param select_name_group: вибрана група
        @param click_num_s: тип тижня - Чисельник/Знаменник
        @param select_weekday: день тижня. Пн - Пт
        @param all_group: Список усіх груп в БД
        @return:
        """
        name_group = self.name_group
        basic_text_btn = self.basic_text_btn
        basic_callback_data_list = self.callback_data_list

        type_inl_btn = self.main_btn_inline_callback[1]

        list_name_group = all_group  # get list group with db

        # створюємо базову структуру клавіатури
        text_btn_list = [
            basic_text_btn[0], self.__select_btn(basic_text_btn[-1]), *list_name_group
        ]

        group_callback_data_list = [
            ScheduleAnotherGroupCBData(
                my_group=name_group, type_inl_btn=type_inl_btn, select_my_g=group) for group in list_name_group]

        callback_data_list = [*basic_callback_data_list, *group_callback_data_list]

        adjust = zip_adjust(1, 1, 5)

        if select_name_group is not None:  # якщо натиснули на назву групи
            text_btn_list, callback_data_list, adjust = self.__create_kb_with_select_group(
                text_btn_list, callback_data_list, adjust, select_name_group, type_inl_btn, click_num_s, select_weekday
            )

        return _inline_builder(
            text_btn_args=text_btn_list,
            callback_data_btn_args=callback_data_list,
            adjust=adjust
        ).as_markup(resize_keyboard=True)


class ForStudentIKb(BaseButton):
    back_inline_callback: tuple = ('back',)
    back_inl_btn: dict = {
        back_inline_callback[0]: 'Назад',
    }

    @staticmethod
    @cached(ttl=TTL_CACHE, max_size=256)
    def first_letter(list_letter=Optional[list]):
        from utils.tools import sort
        text_btn_list = sort(list_letter, key_list=UA_RUS_EN)
        callback_data_list = [FoundTeacherCBData(
            type_inl_btn='letter', letter=letter, level=1) for letter in text_btn_list]

        return _inline_builder(
            text_btn_args=text_btn_list,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(5)
        ).as_markup(resize_keyboard=True)

    def list_teacher(self, letter: str):
        text_btn_list = sorted(Schedule().get_teacher_from_first_letter(letter=letter))
        callback_data_list = [FoundTeacherCBData(
            type_inl_btn='teacher', letter=letter, teacher=teacher, level=2) for teacher in text_btn_list]
        text_btn_list += self.back_inl_btn.values()

        callback_data_list += [FoundTeacherCBData(type_inl_btn=self.back_inline_callback[0], level=0)]
        len_list: int = len(text_btn_list)
        return _inline_builder(
            text_btn_args=text_btn_list,
            callback_data_btn_args=callback_data_list,
            adjust=zip_adjust(*(2,) * ((len_list - 2) // 2), *(1,) * ((len_list - 2) % 2), 1)
        ).as_markup(resize_keyboard=True)
