import asyncio

from aiogram import exceptions

from utils.module.tasking import TaskManager

__MAX_INSTANCES = 29  # 29 message in 1 second

# import queue
queue = asyncio.Queue()

private_chat_tm = TaskManager()

private_chat_tm.include(queue, max_instances=__MAX_INSTANCES)
