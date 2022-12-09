import hashlib
import inspect
import logging
import os
import sys
from typing import Optional

from aiogram.fsm.state import StatesGroup, State


def remove_state(*args, states_group: Optional = None) -> Optional[set | list | str]:
    """
    Видаляє передані State або StatesGroup

    Args:
        *args: State або StateGroup, які потрібно видалити
        states_group: З якої StatesGroup потрібно виключити State

    Returns:
        None
    """
    if not isinstance(states_group, (list, tuple, set, frozenset)) and not type(states_group) == type(
            StatesGroup) and states_group is not None:
        raise TypeError("unsupported type(s). StateGroup is expected")

    if not args and not states_group:
        return '*'

    #  якщо ми передали StateGroup то запакуємо в set()
    if type(states_group) == type(StatesGroup):
        states_group = {states_group}

    if isinstance(states_group, (list, tuple, frozenset)):
        states_group = {state for state in states_group}

    # отримуємо state
    set_state = {state for state in args if isinstance(state, State)}
    # state_group - які ми передали з тих, які потрібно видалити
    set_state_group = set(args) - set_state
    if states_group:
        # видалимо state_group які ми передали
        list_state_group = states_group - set_state_group
    else:
        # Збираємо усі state_group окрім {State, StatesGroup} | set_state_group
        list_state_group = {
            cls_obj for cls_name, cls_obj in inspect.getmembers(sys.modules['states.default_state'])
            if inspect.isclass(cls_obj) and cls_obj not in {State, StatesGroup} | set_state_group
        }
    # отримуємо тепер state із list_state_group окрім set_state
    return [state for state_group in list_state_group for state in state_group if state not in set_state] + [None]


def sort(lst: Optional[list | tuple | set | frozenset],
         key=None, reverse: Optional[bool] = False,
         key_list: Optional[list | tuple] = None) -> Optional[list | tuple | set | frozenset]:
    if key is not None:
        return sorted(lst, key=key, reverse=reverse)

    if key_list is None:
        return sorted(lst, reverse=reverse)

    if isinstance(key_list, frozenset) or isinstance(key_list, set):
        raise TypeError(
            f"The data type must be ordered. "
            f"The variable \"key_list\" must be of type list or tuple - {key_list}"
        )
    elif not isinstance(key_list, list) and not isinstance(key_list, tuple):
        raise TypeError(
            f"The variable \"key_list\" must be of type list or tuple - {key_list}"
        )
    return sorted(lst, key=lambda e: key_list.index(e[0]), reverse=reverse)  # відсортуємо список lst по іншому списку


def remove_duplicate(lst: Optional[list | tuple | set | frozenset]):
    """Видаляємо дублікати зі списку"""
    seen = {}
    return [seen.setdefault(x, x) for x in lst if x not in seen]


def convert_text_to_markdown_(text: Optional[str]) -> Optional[str]:
    """Конвертуємо звичайний текст у формат стилю markdown за всіма нормами"""
    specific_characters = {'_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'}

    for character in specific_characters:
        text = text.replace(character, '\\' + character)

    return text


def unpacked(lst: Optional[list]):
    """
        Unpacks a multi-level list into a 1-level list

    Args:
        lst: Multi-level list

    Returns:
        1-level list

    """
    while lst:
        sublist = lst.pop(0)
        if isinstance(sublist, list):
            lst = sublist + lst
        else:
            yield sublist


def get_dir_hash(path_to_dir: Optional[str]) -> Optional[str]:
    """
        Get hash-sum in dir

    Args:
        path_to_dir: Example - /directory

    Returns:
        hash suma

    """
    dir_hash = ''
    for file in os.listdir(path_to_dir):
        with open('{}/{}'.format(path_to_dir, file), "rb") as open_file:
            file_hash = hashlib.sha256()
            while chunk := open_file.read(8192):
                file_hash.update(chunk)

        dir_hash += file_hash.hexdigest()
    return hashlib.sha256(dir_hash.encode('utf8')).hexdigest()


async def remove_file_in_dir(path_to_dir: Optional[str]) -> Optional[bool]:
    """
        Remove file in path

    Args:
        path_to_dir: Example - /directory

    Returns:
        Note
    """
    if not os.path.exists(path_to_dir):
        return False
    logging.debug("Start remove file and dir in dir {}".format(path_to_dir))
    for file in os.listdir(path_to_dir):
        os.remove(os.path.join(path_to_dir, file))
    # os.rmdir(path_to_dir)

    logging.debug("Remove files in dir {}".format(path_to_dir))

    return True


async def create_dir(path_to_dir: Optional[str]) -> Optional[bool]:
    """
        Remove file in path

    Args:
        path_to_dir: Example - /directory

    Returns:
        Note
    """
    if os.path.exists(path_to_dir):
        logging.debug("Dir exist {}".format(path_to_dir))
        return False

    os.mkdir(path=path_to_dir)
    logging.debug("Create dir {}".format(path_to_dir))

    return True


def abc(value: int):
    '''Convert number to ABC'''
    abc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if value < 1:
        raise ValueError('Number low 1')
    result = ''
    len_abc = len(abc)
    while value > len_abc:
        result += abc[value % len_abc - 1]
        value = value // len_abc
    result += abc[value - 1]
    return result[::-1]
