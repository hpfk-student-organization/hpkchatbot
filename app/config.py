""" Файл з конфігурацією """
import os

from dotenv import load_dotenv

# include venv-param
__NAME_DIR = lambda path: os.path.join(os.path.dirname(__file__), path)

__NAME_VENV_DIR = '../.env'

dotenv_path = __NAME_DIR(__NAME_VENV_DIR)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

API_TOKEN = os.environ['API_TOKEN']  # Token aiogram bot

DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_CHARSET = os.environ['DB_CHARSET']

REDIS_DB_HOST = os.environ['REDIS_HOST']
REDIS_DB_PORT = os.environ['REDIS_PORT']
REDIS_DB_USER = os.environ['REDIS_USER']
REDIS_DB_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_DB_NAME = os.environ['REDIS_DB_NAME']

WEATHER_TOKEN = os.environ['WEATHER_TOKEN']  # API token weather

ID_GROUP_ADMIN = os.environ['ID_GROUP_ADMIN']  # Group admin

# System parameters #

PATH_TO_PHOTO_REPLACEMENTS = __NAME_DIR('data/photo/replacements/')
PATH_TO_PHOTO_TIME_BOOK = __NAME_DIR('data/photo/time_book/')
PATH_TO_FILE_SCHEDULE = __NAME_DIR('data/schedule')

LIMIT_SEND_PHOTO = 10

VENV_DIR_NAME = 'venv'

"""BROWSER_HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'accept': '*/*'
}"""
URL_REPLACEMENTS = 'https://hpk.edu.ua/replacements'