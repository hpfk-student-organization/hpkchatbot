import redis
from aiogram.fsm.storage.redis import RedisStorage


class BaseRedis:

    def __init__(self, host: str, port: int | str, user: str, password: str, db: str):
        """Інцілізуєм підключення"""
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = db

        self.url = "redis://{user}:{password}@{host}:{port}/{db}".format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            db=self.db
        )

    def connect(self):
        """Підключаємося redis://user:password@host:port/db"""
        return RedisStorage.from_url(
            url=self.url,
            connection_kwargs={"decode_responses": True}
        )

    def ping(self):
        try:
            return redis.Redis.from_url(url=self.url).ping()
        except redis.exceptions.ConnectionError:
            return False
