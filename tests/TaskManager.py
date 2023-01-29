import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.module.tasking import TaskManager

queue = asyncio.Queue()
scheduler = AsyncIOScheduler()


async def func(i):
    # Your asynchronous function here
    print(i)


async def main():
    task_manager = TaskManager()

    task_manager.include(queue, max_instances=6)
    for i in range(25):
        await queue.put(func(i))
    task_manager.start()

    while True:
        print('I am monitoring the thread every 5 seconds')
        await asyncio.sleep(5)


if __name__ == '__main__':
    asyncio.run(main())
