# базовий модуль з основними полями
from typing import Optional

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.module.keyboard import zip_builder


def _inline_builder(text_btn_args: Optional[tuple | list],
                    callback_data_btn_args: Optional[tuple | list],
                    adjust: Optional[tuple] = None,
                    builder: Optional[InlineKeyboardBuilder] = None,
                    method_create: Optional[str] = 'add') -> InlineKeyboardMarkup | InlineKeyboardBuilder:
    """inline builder"""
    if not builder:
        builder = InlineKeyboardBuilder()
    return zip_builder(
        text_btn_args=text_btn_args,
        builder=builder,
        callback_data_btn_args=callback_data_btn_args,
        adjust=adjust,
        method_create=method_create
    )


class BaseButton:
    back_btn = 'Назад'


class BaseCBData:
    """Базовий клас, який зберігає рівень основні поля усіх класів CallBack"""
    pass
