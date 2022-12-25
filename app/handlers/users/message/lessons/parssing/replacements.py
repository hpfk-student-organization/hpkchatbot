import datetime
from loguru import logger
import re
from typing import Optional, List

import aiogram
from bs4 import BeautifulSoup

from utils.mysql import Replacements


def __get_text(html_tag):
    """
    Отримуємо з html тегу текст

    @param html_tag:
    @return:
    """
    return html_tag.get_text()


def __replace_to_space(item: str):
    """
    Замінює усі символи не стандартного пробілу на символи звичайного пробілу

    @param item:
    @return:
    """
    old = '\xa0'
    new = ''
    return item.replace(old, new)


def __get_information_for_replacements(soup: BeautifulSoup) -> Optional[list]:
    """
    Парсить систему інформацію, на який день заміни, і чи тиждень знаменник чи чисельник

    @param soup:
    @return:
    """
    limit = 2
    result = soup.find_all('p', limit=limit)
    return list(map(__get_text, result))


def __get_news_replacements(soup: BeautifulSoup) -> Optional[list]:
    """
    Парсить оголошення та додаткові новини, типу:

    Чергові викладачі : Павлова М.Б. Бєльський А.В.
    Четверті пари проводяться за розкладом другої пари вівторка (чисельник)

    @param soup:
    @return:
    """

    news = soup.find_all('td')
    tmp = news[6].get_text()
    if not tmp.isspace():
        return [tmp]

    tmp = news[7].get_text()
    if not tmp.isspace():
        return [tmp]

    return []


def __get_main_table_with_replacements_tomorrow(soup: BeautifulSoup) -> Optional[list]:
    """
    Парсить самі заміни із сайту

    @param soup:
    @return:
    """
    result = soup.find_all('tr')[2:]
    return list(map(__get_text, result))


def __unpack_group(
        name_group: str, number_lesson: str, old_teacher: str, name_subject: str, new_teacher: str, room: str
) -> List[List[str]]:
    unpack_name_group, *last_name_group = name_group.split(',')
    prefix, first_name_group = re.split(r'-', unpack_name_group)

    list_new_name_group = []
    for _name_group in (first_name_group, *last_name_group):
        list_new_name_group.append(
            ['{0}-{1}'.format(prefix, _name_group), number_lesson, old_teacher, name_subject, new_teacher, room]
        )
    return list_new_name_group


def __formation_main_table_replacement(list_replacements: Optional[list[str]]):
    """
        Розпаковуємо коректно список замін, на частини

    @param list_replacements:
    @return:
    """
    new_list_replacements = []
    last_group: str = ''
    for item_replacements in list_replacements:  # 'КІ-222\n5-6\n\nМатематика\nКозубець\n124'
        item_replacements = item_replacements[1:-1].replace('\n\n', '\n \n')
        if not len(item_replacements) - 7:  # пропускаємо порожній рядок із замінами, за допомогою підрахунку символів
            logger.debug('Skip one null replacements')
            continue
        group, number_lesson, old_teacher, name_subject, new_teacher, room, *another = item_replacements.split('\n')
        if group:  # на порожнє поле із групою встановлюємо попереднє значення назви групи
            last_group = group
        if last_group.count(','):  # якщо міститься запис типу КІ-191,192 перетворюємо в КІ-191 та КІ-192
            little_replacements = __unpack_group(last_group, number_lesson, old_teacher, name_subject, new_teacher,
                                                 room)
            for item in little_replacements:  # дублюємо заміни для двох груп, якщо є запис групи типу КІ-191,192
                new_list_replacements.append(item)
            continue
        new_list_replacements.append([last_group, number_lesson, old_teacher, name_subject, new_teacher, room])
    return new_list_replacements


async def parsing_replacements(html_code: Optional[str], bot: aiogram.Bot):
    """
    Здійснюємо пошук

    @param bot:
    @param html_code:
    @return:
    """
    soup = BeautifulSoup(html_code, 'html.parser')
    # logger.debug('Search new replacements...')
    information_for_replacements = __get_information_for_replacements(soup)

    last_day_replacements = ''
    info_of_replacements = Replacements().get_info_replacements_with_table()
    if len(info_of_replacements):
        last_day_replacements = info_of_replacements[0]
    if len(information_for_replacements) and information_for_replacements[0] == last_day_replacements:
        # logger.debug('Not found new tomorrow replacements')
        return

    logger.info('Found new tomorrow replacements ')
    Replacements().clear_all_table_with_replacements()
    logger.info('Clear old replacements')

    # main_table_with_replacements_tomorrow: list = list(map(__get_text, list_with_tag_about_replacements))[6:]

    # if main_table_with_replacements_tomorrow.count(new_replacements):
    #    main_table_with_replacements_tomorrow.remove(new_replacements)

    news_replacements = list(map(__replace_to_space, __get_news_replacements(soup)))
    main_table_with_replacements_tomorrow = list(
        map(__replace_to_space, __get_main_table_with_replacements_tomorrow(soup))
    )
    main_table_with_replacements_tomorrow = __formation_main_table_replacement(main_table_with_replacements_tomorrow)

    logger.debug('Start save information of replacements in databases')
    Replacements().insert_all_replacements_in_table(all_replacements=main_table_with_replacements_tomorrow)
    Replacements().insert_info_replacements_in_table(info_of_replacements=information_for_replacements)
    Replacements().insert_news_replacements_in_table(news_of_replacements=news_replacements)
    logger.info('Save finish information')

    list_user_sub = Replacements().get_subscription_who_get_replacements_from_site()
    await send_new_replacements_for_sub(bot=bot, list_user_sub=list_user_sub)


async def send_new_replacements_for_sub(bot: aiogram.Bot, list_user_sub: List[int | str]):
    """Send new replacements in sub from site"""
    from scheduler.private_chat import queue, scheduler, jobs_id
    from handlers.users.message.lessons.get_replacements import create_message_for_replacements_with_site
    scheduler.resume_job(jobs_id[0])
    for user_id in list_user_sub:
        name_group = Replacements().get_subscription_name_group(telegram_id=user_id)

        replacements_from_site_message_text = create_message_for_replacements_with_site(
            name_group=name_group)
        title_text = 'Нові заміни, станом на'

        await queue.put(
            bot.send_message(
                chat_id=user_id,
                text='{0} {1}\n\n{2}'.format(
                    title_text, datetime.datetime.now().strftime('%H:%M'), replacements_from_site_message_text
                )
            )
        )
    # обновимо інформацію для користувачів, хто коли отримав заміни і які саме
    Replacements().update_last_time_send_replacements(2)
