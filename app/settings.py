import sys
from os.path import abspath, dirname, join

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

import config
from utils.base_redis import BaseRedis
from utils.module.redis import RedisGlobalStorage, RedisGlobalStorageBasic

base_dir = abspath(dirname(__file__))
logs_target_info = abspath(join(base_dir, 'logs', 'info.log'))
logs_target_error = abspath(join(base_dir, 'logs', 'error.log'))


format_text = '{time} {level} {message}'
__config = {
    "handlers": [
        {"sink": sys.stdout, "format": format_text, "level":"INFO"},
    ],
    "extra": {"user": "someone"}
}
# logger.configure(**__config )
# info handler
logger.add(
    logs_target_info,
    format=format_text,
    level='INFO',
    rotation="1 week",
    compression="zip"
)
# error handler
logger.add(
    logs_target_error,
    format=format_text,
    level='ERROR',
    rotation="1 week",
    compression="zip"
)

bot = Bot(token=config.API_TOKEN, parse_mode='HTML')  # parse_mode='MarkdownV2')

storage = BaseRedis(host=config.REDIS_DB_HOST, port=config.REDIS_DB_PORT, db=config.REDIS_DB_NAME,
                    user=config.REDIS_DB_USER, password=config.REDIS_DB_PASSWORD)
if storage.ping():
    storage = storage.connect()
else:
    logger.warning("Using Memory Storage!")
    storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Connect to standard redis for save global parameter

global_storage = RedisGlobalStorage(
    connect_to_redis=RedisGlobalStorageBasic(
        host=config.REDIS_DB_HOST, port=config.REDIS_DB_PORT,
        db=config.REDIS_DB_NAME, user=config.REDIS_DB_USER, password=config.REDIS_DB_PASSWORD
    ).connect(),
    prefix=bot.token
)

# scheduler
redis_scheduler = RedisJobStore(
    db=0,

)
scheduler = AsyncIOScheduler()
