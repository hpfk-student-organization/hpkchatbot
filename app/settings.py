import logging
from logging.config import dictConfig
from os.path import abspath, dirname, join

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import config
from utils.base_redis import BaseRedis
from utils.module.redis import RedisGlobalStorage, RedisGlobalStorageBasic

base_dir = abspath(dirname(__file__))
logs_target_info = abspath(join(base_dir, 'logs', 'info.log'))
logs_target_error = abspath(join(base_dir, 'logs', 'error.log'))

__logging_schema = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'class': 'logging.Formatter',
            # Optional: setting format time
            'datefmt': '%d %b %y %H:%M:%S',
            'format': '[%(levelname)s:%(asctime)s]: \t%(message)s'
            # 'format': '[%(levelname)s:%(asctime)s] - %(filename)s:%(lineno)d]: %(message)s'
            # 'format': '[%(levelname)s:%(asctime)s] %(message)s'
        },
    },
    # Handlers use the formatter names declared above
    'handlers': {
        # Name of handler
        'console': {
            # The class of logger. A mixture of logging.config.dictConfig() and
            # logger class-specific keyword arguments (kwargs) are passed in here.
            'class': 'logging.StreamHandler',
            # 'class': 'logging.apscheduler.executors.default',

            # This is the formatter name declared above
            'formatter': 'standard',
            'level': 'DEBUG',  # DEBUG
            # The default is stderr
            'stream': 'ext://sys.stdout'
        },

        # Same as the StreamHandler example above, but with different
        # handler-specific kwargs.
        'file_info': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'level': 'WARNING',
            'filename': logs_target_info,
            'mode': 'a',
            'encoding': 'utf-8',
            'maxBytes': 10000000,
            'backupCount': 4
        },
        'file_error': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'filename': logs_target_error,
            'mode': 'a',
            'encoding': 'utf-8',
            'maxBytes': 50000000,
            'backupCount': 4
        }
    },
    # Loggers use the handler names declared above
    'loggers': {
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'file_info', 'file_error', ],
        }
    },

}

# include config logger
dictConfig(__logging_schema)

bot = Bot(token=config.API_TOKEN, parse_mode='HTML')  # parse_mode='MarkdownV2')

storage = BaseRedis(host=config.REDIS_DB_HOST, port=config.REDIS_DB_PORT, db=config.REDIS_DB_NAME,
                    user=config.REDIS_DB_USER, password=config.REDIS_DB_PASSWORD)
if storage.ping():
    storage = storage.connect()
else:
    logging.warning("Using Memory Storage!")
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
