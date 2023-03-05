import hashlib

from loguru import logger
import os
from typing import Optional, List


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
    logger.debug("Start remove file and dir in dir {}".format(path_to_dir))
    for file in os.listdir(path_to_dir):
        os.remove(os.path.join(path_to_dir, file))
    # os.rmdir(path_to_dir)

    logger.debug("Remove files in dir {}".format(path_to_dir))

    return True


def create_dir(path_to_dir: Optional[str]) -> Optional[bool]:
    """
        Remove file in path

    Args:
        path_to_dir: Example - /directory

    Returns:
        Note
    """
    if os.path.exists(path_to_dir):
        logger.debug("Dir exist {}".format(path_to_dir))
        return False

    os.makedirs(path_to_dir)
    logger.debug("Create dir {}".format(path_to_dir))

    return True


def check_and_create_dir(list_of_path: List[str]):
    for path in list_of_path:
        create_dir(path)
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
