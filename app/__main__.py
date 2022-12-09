import asyncio

import logging

from settings import storage, dp, bot, scheduler


async def on_shutdown():
    """Виконуватися коли будемо зупиняти бота"""
    logging.debug("Scheduler storage stopped - Ok")
    await bot.session.close()
    logging.debug("Bot stopped - Ok")
    await storage.close()
    logging.debug("Redis storage stopped - Ok")
    scheduler.shutdown()


async def on_startup():
    """Під час запуску бота"""
    from scheduler.replacements import add_job, jobs_id
    await add_job(jobs_id[0], bot)
    # scheduler.start()
    logging.debug('Starting process start to main commands for bots...')
    logging.info('Bot start - OK')


async def main() -> None:
    # logging.getLogger('apscheduler.executors.default').setLevel(logging.WARNING)

    logging.debug('Include routers in Dispatcher')

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
