# модуль, який допомагає виконувати кілька запускати кілька паралельних функцій з asyncio.Queue

import asyncio
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger


class TaskManager:
    __max_instances = 1
    __result_run = dict()

    __queue_entry = False

    def __init__(self):
        self.queue = asyncio.Queue()
        self._scheduler = AsyncIOScheduler()

    def __del__(self):
        self._scheduler.shutdown()

    @property
    def scheduler(self):
        return self._scheduler.shutdown(wait=True)

    async def __run_tasks(self):
        tasks = set()

        for _ in range(self.__max_instances):
            if self.queue.empty():
                self.__queue_entry = True
                break

            tasks.add(asyncio.create_task(await self.queue.get()))

        while tasks:
            result_task = await tasks.pop()
            num_value = self.__result_run.get(result_task, 0)
            self.__result_run.update({result_task: num_value + 1})

        if self.__queue_entry:
            self._scheduler.shutdown(wait=True)
            logger.info("Task finish. Result: {}".format(
                self.__result_run
            ))

    def include(self, queue: asyncio.Queue, max_instances: Optional[int] = None):
        """
        Включає створену раніше чергу

        @param max_instances:
        @param queue:
        @return:
        """
        self.queue = queue

        if max_instances is None:
            max_instances = 1
        self.__max_instances = max_instances

    def start(self, paused=False):
        """
        Start run task

        @return:
        """
        self._scheduler.add_job(self.__run_tasks, IntervalTrigger(), seconds=1)

        self.__result_run = dict()
        self.__queue_entry = False

        if not self._scheduler.state:
            self._scheduler.start(paused)
