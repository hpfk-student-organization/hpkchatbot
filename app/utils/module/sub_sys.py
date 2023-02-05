"""

This module is had standard function for best experiences

"""

from typing import Optional, Any


def get_name(get_value: Optional[bool] = None, **kwargs):
    name = tuple(kwargs.keys())[0]
    if get_value:
        return name, kwargs.get(name)
    return name


def is_ls_ft(parameter: Optional[Any]):
    """
        Checking `parameter` on list or set or frozenset or tuple

    Args:
        parameter:

    Returns:

    """
    return type(parameter) in [list, set, frozenset, tuple]
