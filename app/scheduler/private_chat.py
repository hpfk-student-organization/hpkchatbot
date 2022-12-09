import asyncio

from aiogram import exceptions
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from settings import scheduler

__MAX_INSTANCES = 29
__LIMIT_SEND_MESSAGE_PRIVATE_CHAT = 1 / __MAX_INSTANCES  # 20 message in 1 second

# import queue
queue = asyncio.Queue()

jobs_id = ('private_chat',)


async def send_message(_queue: asyncio.Queue, _scheduler: AsyncIOScheduler, _job_id: str):
    if not _queue.empty():
        task = await _queue.get()
        await __fish_except(task)
        _queue.task_done()
        return
    _scheduler.pause_job(_job_id)


async def __fish_except(task):
    """Run to task"""
    try:
        await task
    except exceptions.TelegramForbiddenError:
        pass


scheduler.add_job(
    func=send_message,
    args=[queue, scheduler, jobs_id[0]],
    trigger=IntervalTrigger(),
    max_instances=__MAX_INSTANCES,
    id=jobs_id[0]
)
