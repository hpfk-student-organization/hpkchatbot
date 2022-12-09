from typing import Any, Dict, Optional

import aioredis

from utils.module.sub_sys import is_ls_ft
from utils.tools import unpacked

_SET_TYPES = ('int', 'str', 'bool', 'NoneType', '/list', 'list/')


class RedisGlobalStorageBasic:
    """RedisGlobalStorageBasic manages basic redis"""

    def __init__(self, host: str, port: int | str, user: str, password: str, db: str):
        """Інцілізуєм підключення"""
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = db

    def connect(self):
        return aioredis.from_url(
            url="redis://{user}:{password}@{host}:{port}/{db}".format(
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                db=self.db
            ),
            decode_responses=True
        )


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


class RedisGlobalStorage:
    # Standard connect to redis
    redis: aioredis.client.Redis

    def __init__(self, connect_to_redis, prefix: Optional[str] = ''):
        self.redis = connect_to_redis
        self.prefix = prefix

    async def set_data(
            self,
            **kwargs: Any
    ) -> Dict[str, Any]:
        """None, bool, str, int, double, list"""

        list_keys_and_values = kwargs.items()
        for _, values in list_keys_and_values:
            for typ in _SET_TYPES:
                # Check correct values
                if is_ls_ft(values) and typ in unpacked(list(values)) or typ == values:
                    raise ValueError(f'Values is not exists worms with list - {_SET_TYPES}')

        for key, values in list_keys_and_values:
            # Remove key, if key is exists
            if await self.redis.exists('{0}:{1}'.format(self.prefix, key)):
                await self.redis.delete('{0}:{1}'.format(self.prefix, key))

            for list_value in tuple(_unpacked(values)):
                await self.redis.rpush('{0}:{1}'.format(self.prefix, key), list_value)
        return kwargs

    async def get_data(
            self,
            key=Optional[str]
    ):

        values = await self.redis.lrange('{0}:{1}'.format(self.prefix, key), 0, -1)

        return _packed(values)

    async def clean_data(
            self,
            key=Optional[str]
    ):
        """
            Clean data in redis

        Args:
            key:

        Returns:

        """
        await self.redis.delete('{0}:{1}'.format(self.prefix, key))
