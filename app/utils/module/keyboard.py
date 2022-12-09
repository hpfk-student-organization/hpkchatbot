from typing import Optional

from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def zip_adjust(*args: Optional[int], repeat=False) -> ReplyKeyboardBuilder.adjust:
    """Zip adjust - допомагає передати декілька параметрів"""

    return *(item for item in args if item), repeat


def zip_builder(text_btn_args: Optional[tuple[str]],
                builder: Optional[ReplyKeyboardBuilder | InlineKeyboardBuilder] = None,
                callback_data_btn_args: Optional[tuple[CallbackData]] = None,
                method_create: Optional[str] = 'add',
                adjust: Optional[tuple] = None) -> ReplyKeyboardBuilder | InlineKeyboardBuilder:
    """
    Упаковує, архівує, створує кнопки типу ReplyKeyboardBuilder або InlineKeyboardBuilder

    Args:
        text_btn_args: Текстовий назви кнопок
        builder: Тип клавіатури. Базовий чи inline
        callback_data_btn_args: callback_data кнопок. Має співпадати по кількості
        method_create: По стандарту ми додаємо по порядку клавіатури
        adjust: Структура розташування кнопок

    Returns:

    """
    # перевірка коректності даних
    if not (isinstance(builder, ReplyKeyboardBuilder) or isinstance(builder, InlineKeyboardBuilder)):
        raise TypeError(f"The builder is not None")
    elif not (isinstance(text_btn_args, tuple) or isinstance(text_btn_args, list)):
        raise TypeError(f"The text_btn_args not is tuple or list")
    elif not text_btn_args:
        raise ValueError(f"There must be more than 1 buttons")
    elif callback_data_btn_args and not len(text_btn_args) == len(callback_data_btn_args):
        raise ValueError(f"The number of items must match")

    callback_data_btn = None
    for index in range(len(text_btn_args)):
        text_btn = text_btn_args[index]

        if callback_data_btn_args:
            callback_data_btn = callback_data_btn_args[index]
        if not isinstance(text_btn, str):
            raise TypeError(f"The name of the button should be of type str, not type {type(text_btn)} - \"{text_btn}\"")

        if isinstance(builder, ReplyKeyboardBuilder):
            kb_button = KeyboardButton(text=text_btn)
        else:
            kb_button = InlineKeyboardButton(text=text_btn, callback_data=callback_data_btn.pack())

        if method_create == 'add':
            builder.add(kb_button)
        elif method_create == 'row':
            builder.row(kb_button)

    if adjust:
        builder.adjust(*adjust[:-1], repeat=adjust[-1])
    return builder
