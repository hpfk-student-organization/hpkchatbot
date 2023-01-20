
import aiogram
from apscheduler.triggers.interval import IntervalTrigger

import config
from handlers.users.message.lessons.parssing.replacements import parsing_replacements
from settings import scheduler

jobs_id = ('replacements',)

__MAX_INSTANCES = 1
__seconds = 15  # через скільки шукати


async def trigger_for_passing_replacements(_bot: aiogram.Bot):
    """Трігер для перевірки наявності нових змін"""
    from utils.module.webTool import WebTool
    request = WebTool(url=config.URL_REPLACEMENTS)
    html_content = await request.get_html_content()
    await parsing_replacements(html_code=html_content, bot=_bot)


async def add_job(_jobs_id, _bot: aiogram.Bot):
    scheduler.add_job(
        func=trigger_for_passing_replacements,
        args=[_bot],
        trigger=IntervalTrigger(
            seconds=__seconds
        ),
        max_instances=__MAX_INSTANCES,
        id=_jobs_id
    )



