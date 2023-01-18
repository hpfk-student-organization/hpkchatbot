import asyncio

from loguru import logger

import config
from settings import storage, dp, bot, scheduler


async def on_shutdown():
    """Виконуватися коли будемо зупиняти бота"""

    logger.debug("Scheduler storage stopped - Ok")
    await bot.session.close()
    logger.debug("Bot stopped - Ok")
    await storage.close()
    logger.debug("Redis storage stopped - Ok")
    scheduler.shutdown()


async def on_startup():
    """Під час запуску бота"""

    from scheduler.replacements import add_job, jobs_id
    await add_job(jobs_id[0], bot)
    scheduler.start()
    logger.debug('Starting process start to main commands for bots...')
    logger.info('Bot start - OK')

    from utils.tools import check_and_create_dir
    list_path = [config.PATH_TO_PHOTO_REPLACEMENTS, config.PATH_TO_PHOTO_TIME_BOOK, config.PATH_TO_FILE_SCHEDULE]
    check_and_create_dir(list_path)

    await bot.send_message(chat_id=config.ID_GROUP_ADMIN, text='Start bot - OK.')


@logger.catch()
async def main() -> None:
    logger.debug('Include routers in Dispatcher')

    from handlers import router_in_chat, router_in_private, router_e, router_for_admin

    dp.include_router(router_e)
    dp.include_router(router_in_chat)
    dp.include_router(router_for_admin)
    dp.include_router(router_in_private)

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
