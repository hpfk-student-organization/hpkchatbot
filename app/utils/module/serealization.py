# not using and not working
from typing import Optional

from utils.module.sub_sys import is_ls_ft

_SET_TYPES = ('int', 'str', 'bool', 'NoneType', '/list', 'list/')


def serialize(data):
    """Перетворює в рядковий формат """
    result = []
    for item in data:
        if item is None:
            result.extend([type(item).__name__, "None"])
        elif (types := type(item)) == dict:
            ValueError('Not support {0}'.format(types.__name__))

        elif (types := type(item)) in (list, tuple, set, frozenset):
            result.append('/' + types.__name__)
            result.extend(serialize(item))
            result.append(types.__name__ + '/')
        else:
            result.extend([type(item).__name__, str(item)])
    types = type(data).__name__
    return result


def deserialize(input_list):
    output_list = []
    i = 0
    while i < len(input_list):
        if input_list[i] == '/list':
            output_list.append(deserialize(input_list[i + 1:]))
            break
        elif input_list[i] == '/tuple':
            output_list.append(tuple(deserialize(input_list[i + 1:])))
            break
        elif input_list[i] == 'int':
            output_list.append(int(input_list[i + 1]))
            i += 2
        elif input_list[i] == 'float':
            output_list.append(float(input_list[i + 1]))
            i += 2
        elif input_list[i] == 'str':
            output_list.append(input_list[i + 1])
            i += 2
        elif input_list[i] == 'bool':
            output_list.append(input_list[i + 1] == 'True')
            i += 2
        elif input_list[i] == 'list/':
            output_list.append([])
            i += 1
        elif input_list[i] == 'tuple/':
            output_list.append(())
            i += 1
        elif input_list[i] == 'None':
            output_list.append(None)
            i += 1
    return output_list


def _unpacked(lst: Optional[list]):
    """
        Packs and formatting to redis date format

    Args:
        lst:

    Returns:


    """
    set_name_type = '{}'.format(str(type(lst)).split("'")[1])
    if not is_ls_ft(lst):
        yield set_name_type
        yield str(lst)
        return

    lst = list(lst)
    lst = [f'/{set_name_type}'] + lst + [f'{set_name_type}/']
    while lst:

        sublist = lst.pop(0)
        if is_ls_ft(sublist):
            sublist = list(sublist)
            lst = ['/list'] + sublist + ['list/'] + lst
        else:
            if sublist not in _SET_TYPES:
                yield str(type(sublist)).split("'")[1]
            yield str(sublist)


def _packed(lst: Optional[list]):
    """['/list', 'int', '1', 'int', '2', 'int', '3', '/list', 'int', '3', 'int', '1', 'list/', 'int', '2', 'list/']"""
    """[1, 2, 3, [3, 1], 2]"""
    """[[]]"""
    """['list','list']"""
    pack_list = None

    next_type = ''
    while lst:
        sublist = lst.pop(0)
        match sublist:
            case '/list':
                if pack_list is None:
                    pack_list = list()
                    continue
                pack_list.append(list())
                pack_list[-1].extend(_packed(lst))
            case 'list/':
                break
            case _:
                if sublist in _SET_TYPES:
                    next_type = sublist
                    continue
                if pack_list is None and len(lst) > 1:
                    # Create list, if len lst is > 1
                    pack_list = list()
                match next_type:
                    case 'int':
                        tmp = int(sublist)
                        if isinstance(pack_list, list):
                            pack_list.append(tmp)
                            continue
                        pack_list = tmp
                    case 'str':
                        tmp = str(sublist)
                        if isinstance(pack_list, list):
                            pack_list.append(tmp)
                            continue
                        pack_list = tmp
                    case 'bool':
                        tmp = bool(sublist)
                        if isinstance(pack_list, list):
                            pack_list.append(tmp)
                            continue
                        pack_list = tmp

                    case 'NoneType':
                        tmp = None
                        if isinstance(pack_list, list):
                            pack_list.append(tmp)
                            continue
                        pack_list = tmp

    return pack_list
