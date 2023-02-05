import ast
from typing import Any, Dict, Optional

import aioredis


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

        for key, values in list_keys_and_values:
            # Remove key, if key is exists
            if await self.redis.exists('{0}:{1}'.format(self.prefix, key)):
                await self.redis.delete('{0}:{1}'.format(self.prefix, key))

            # for list_value in tuple(_unpacked(values)):
            await self.redis.set('{0}:{1}'.format(self.prefix, key), str(values))
        return kwargs

    async def get_data(
            self,
            key=Optional[str]
    ):

        if await self.redis.exists('{0}:{1}'.format(self.prefix, key)):
            values = await self.redis.get('{0}:{1}'.format(self.prefix, key))
            try:
                return ast.literal_eval(values)
            except Exception:
                return values
        return None

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
