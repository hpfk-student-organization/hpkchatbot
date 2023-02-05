import datetime
import json
import random
from typing import Optional, Any, List

import pymysql
import pymysql.cursors

import config
from utils.module import language
from utils.tools import remove_duplicate, sort


def _unpack_all_values_with_dict_old(sql_result: list):
    """
    Not support get key

    Convert sql_request with dict to list format

    Input: [{'key_1': value_1_1, 'key_2': value_1_2}, {'key_1': value_2_1, 'key_2': value_2_2}, ...]

    Output: [[value_1_1, value_2_1, ...] ,[value_1_2, value_2_2, ...]]

    Abstract - [value_first_key, value_second_key, value_last_key...]

    """
    template_list = [list() for _ in range(len(sql_result[-1].keys()))]

    for dict_items in sql_result:
        dict_items_keys = list(dict_items.keys())
        while len(dict_items_keys):  # [key_1, key_2]
            template_list[len(dict_items_keys) - 1].append(dict_items.get(dict_items_keys.pop()))
    if len(template_list) - 1:
        return template_list
    return template_list[0]


def _unpack_all_values_with_dict(cursor, key: bool = False, new_support: bool = False) -> list:
    """

    Convert sql_request with dict to list format

    Input: [{'key_1': value_1_1, 'key_2': value_1_2}, {'key_1': value_2_1, 'key_2': value_2_2}, ...]

    Output with not key_ignore: [[key_1, key_2, ...], [[value_1_1, value_1_2, ...], [value_2_1, value_2_2, ...], ...]

    Output with key_ignore: [[value_1_1, value_1_2, ...], [value_2_1, value_2_2, ...], ...]

    """

    sql_result = cursor.fetchall()
    if not sql_result:
        # if result null
        return []

    if not new_support:  # big count function have another realisation
        return _unpack_all_values_with_dict_old(sql_result)

    list_items_keys = list(sql_result[-1].keys())

    value_list = list()
    for item_value in sql_result:
        item_value: dict
        value_list.append(list(item_value.values()))
    if len(list_items_keys) - 1 and key:
        return [list_items_keys, value_list]
    elif len(list_items_keys) - 1:
        return value_list
    return [item[0] for item in value_list]


def _unpack_list(value: list, index: int):
    if len(value):
        return value[index]
    return value


def _up_string(for_set: Optional[str], name_values: Optional[str], values: Optional[type]) -> Optional[str]:
    """

        For only this function

    Args:
        for_set (object):


    Returns:

    """

    if name_values.count(' '):
        name_values = f'"{name_values}"'
    if isinstance(values, str):
        values = f'"{values}"'

    if values:
        for_set += f'{name_values} = {values}, '

    return for_set


def create_connection(database: Optional[str],
                      user: Optional[str], password: Optional[str],
                      host: Optional[str] = '127.0.0.1', port: int = 3306,
                      charset='utf8mb4', ):
    connection = None
    try:
        connection = pymysql.connect(
            host=host, port=port, user=user, password=password, database=database, charset=charset,
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.err.OperationalError as error:
        raise ConnectionError('Error connect to databases: {0}'.format(error))

    return connection


class BaseMysql:
    _table_replacements = 'subs_replacements'
    _table_users = 'info_users'
    _table_quotes = 'qts_quotes'
    _table_teacher = 'qts_teacher'
    _table_tmp_file_id = 'tmp_file_id'
    _table_files_id = 'files_id'
    _table_file_id_replacements = 'file_id_replacements'
    _table_global_settings = 'global_settings'
    _table_anonim_users = 'anonim_users'
    _table_for_table_replacements = 'table_replacements'
    _table_for_info_replacements = 'table_info_replacements'
    _table_for_news_replacements = 'table_news_replacements'
    _table_holy_text = 'holy_text'
    _table_table_schedule = 'table_schedule'

    def __init__(self):
        #  connect to DB
        self.connection = create_connection(
            database=config.DB_NAME,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            host=config.DB_HOST,
            port=int(config.DB_PORT),
            charset=config.DB_CHARSET
        )


class QuotesTeacher(BaseMysql):
    '''def create_table_test(self):
        """Створимо для тесту таблицю в БД"""
        with cursor as cursor:
            sql = "CREATE TABLE test_table(" \
                  "test_table_id INT PRIMARY KEY AUTO_INCREMENT," \
                  "test_colum INT" \
                  ");"
            cursor.execute(sql)'''

    def select_all_list_teachers(self) -> list:
        """
        Get all teachers from the databases

        Returns: Set teachers

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.title FROM {0}"
            cursor.execute(sql.format(self._table_teacher))

            return list(_unpack_all_values_with_dict(cursor))

    def select_emoji_of_teacher(self, list_teachers: list) -> list:
        """
        Get emoji of teachers from the databases

        Returns: Set teachers

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.title, {0}.emoji FROM {0} WHERE {0}.title IN %s"
            cursor.execute(sql.format(self._table_teacher), (list_teachers,))

            return list(_unpack_all_values_with_dict(cursor, new_support=True))

    def select_all_quotes_with_teacher(self, teacher: str) -> list:
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.text FROM {0} INNER JOIN {1} USING(`teacher_id`) WHERE {1}.title = %s"

            cursor.execute(sql.format(self._table_quotes, self._table_teacher), (teacher,))

            list_quotes = list(_unpack_all_values_with_dict(cursor))
            random.shuffle(list_quotes)
            return list_quotes

    def get_first_letter_with_all_teacher(self) -> Optional[list]:
        with self.connection.cursor() as cursor:
            sql = "SELECT title FROM {0}"
            cursor.execute(sql.format(self._table_teacher))

            return sort(remove_duplicate([teacher[0] for teacher in list(_unpack_all_values_with_dict(cursor))]),
                        key_list=language.UA_RUS_EN)

    def get_all_teacher_with_first_letter(self, first_letter: Optional[str]) -> Optional[list]:
        with self.connection.cursor() as cursor:
            sql = f"SELECT title FROM {self._table_teacher} WHERE title LIKE '{first_letter}%'"
            cursor.execute(sql)

            return sort(list(_unpack_all_values_with_dict(cursor)), key_list=language.UA_RUS_EN)

    def add_new_quotes(self, teacher: Optional[str], text: Optional[str]) -> Optional[None]:
        """
        Add new quotes in databases in tables qts_quotes

        Returns: None

        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (text, teacher_id) VALUES(%s, (SELECT teacher_id FROM {1} WHERE title = %s))"

            cursor.execute(sql.format(self._table_quotes, self._table_teacher), (text, teacher))
            self.connection.commit()

    def is_check_exist_teacher(self, teacher: Optional[str]) -> Optional[bool]:
        """
        Checking teacher in databases

        Args:
            teacher: check to teacher in databases

        Returns:
            True/False - is existed/not is existed

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT `teacher_id` FROM {0} WHERE `title`=%s"

            return bool(cursor.execute(sql.format(self._table_teacher), (teacher,)))

    def add_new_teacher(self, title: Optional[str], emoji: Optional[str] = None) -> Optional[None]:
        """
        INSERT new teacher in tables with all teachers in databases

        Args:
            emoji:
            title: Title new teacher

        Returns: None

        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (`title`, `emoji`) VALUES (%s,%s)"

            cursor.execute(sql.format(self._table_quotes), (title, emoji))
            self.connection.commit()


class Users(BaseMysql):
    """Controls all users"""

    def is_check_exist_user(
            self,
            telegram_id: Optional[int]
    ) -> Optional[bool]:
        """
        Checking user in databases of telegram_id

        Args:
            telegram_id: user id in telegram

        Returns:
            True/False - is existed/not is existed

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT `telegram_id` FROM {0} WHERE `telegram_id`=%s"

            return bool(cursor.execute(sql.format(self._table_users), (telegram_id,)))

    def add_new_user(
            self,
            telegram_id: Optional[int],
            user_old_actions: Optional[str] = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            user_register: Optional[str] = datetime.datetime(2020, 8, 24, 0, 0, 0),
            username: Optional[str] = None,
            terms_of_user: Optional[bool] = False,
            user_admin: Optional[bool] = False,

    ) -> Optional[None]:
        """
        INSERT new user in tables with all users in databases

        Args:


        Returns: None

        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (telegram_id, username, terms_of_user, user_admin, user_register, user_old_actions) " \
                  "VALUES (%s, %s, %s, %s, %s, %s)"

            cursor.execute(
                sql.format(self._table_users),
                (telegram_id, username, terms_of_user, user_admin, user_register, user_old_actions)
            )
            self.connection.commit()

    def update_info_user(
            self,
            telegram_id: Optional[int],
            user_old_actions: Optional[str],
            username: Optional[str]
    ) -> Optional[None]:
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} SET username = %s, user_old_actions=%s  WHERE telegram_id = %s "

            cursor.execute(
                sql.format(self._table_users),
                ( username, user_old_actions,telegram_id)
            )
            self.connection.commit()

    def update_info_user_old(
            self,
            telegram_id: Optional[int],
            user_old_actions: Optional[str] = None,
            user_register: Optional[str] = None,
            username: Optional[str] = None,
            terms_of_user: Optional[bool] = None,
            user_admin: Optional[bool] = None,

    ) -> Optional[None]:
        """
        UPDATE user in tables with all users in databases

        Args:


        Returns: None

        """
        with self.connection.cursor() as cursor:
            str_set_for_mysql = f' username="{username}", '

            str_set_for_mysql = _up_string(str_set_for_mysql, 'user_old_actions', user_old_actions)
            str_set_for_mysql = _up_string(str_set_for_mysql, 'user_register', user_register)
            str_set_for_mysql = _up_string(str_set_for_mysql, 'terms_of_user', terms_of_user)
            str_set_for_mysql = _up_string(str_set_for_mysql, 'user_admin', user_admin)

            sql = "UPDATE {0} SET {1} WHERE telegram_id = %s"

            cursor.execute(sql.format(self._table_users, str_set_for_mysql[:-2]), (telegram_id,))
            self.connection.commit()

    def update_or_add_if_not_exist_new_user(
            self,
            telegram_id: Optional[int],
            user_old_actions: Optional[str] = None,
            user_register: Optional[str] = None,
            username: Optional[str] = None

    ) -> Optional[None]:
        """
        Add new user in to databases, if user not exist in these databases. If user exist to add new user in databases

        Args:
            telegram_id:
            user_register: date user register in system(bot)
            user_old_actions: date last operation in system(bot)
            username: username in telegram(if exist). Default is None
            terms_of_user: status terms of user. Default is False
            user_admin: user is admin? Default in False
        """

        if not self.is_check_exist_user(telegram_id):  # if not user is existed in databases
            # if False - add new user in databases

            # Add new user for column with information
            self.add_new_user(
                telegram_id=telegram_id,
                user_old_actions=user_old_actions,
                user_register=user_register,
                username=username
            )

            return
            # else if user is existed in databases - update info user
        self.update_info_user(
            telegram_id=telegram_id,
            user_old_actions=user_old_actions,
            username=username
        )

    def get_id_all_admin_in_set(self) -> Optional[set]:
        """
         Get set() all id admin in databases

        Returns: set()

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT `telegram_id` FROM `{0}` WHERE `user_admin` = 1"

            cursor.execute(sql.format(self._table_users))
            result = _unpack_all_values_with_dict(cursor)
            return set(result)

    def check_status_terms_of_user(self, telegram_id: Optional[int]) -> Optional[bool]:
        """
        Check in databases status accept terms of user

        Returns: bool()

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.terms_of_user FROM {0} WHERE {0}.telegram_id = %s"

            cursor.execute(sql.format(self._table_users), (telegram_id,))
            return bool(_unpack_list(_unpack_all_values_with_dict(cursor), 0))


class Replacements(BaseMysql):
    """Controls all users"""

    def is_check_exist_user(
            self,
            telegram_id: Optional[int]
    ) -> Optional[bool]:
        """
        Checking user in databases of telegram_id

        Args:
            telegram_id: user id in telegram

        Returns:
            True/False - is existed/not is existed

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id = %s"

            return bool(cursor.execute(sql.format(self._table_replacements, self._table_users), (telegram_id,)))

    def add_new_user_for_replacements(self, telegram_id: Optional[int | str]) -> Optional[None]:
        """
        Add new quotes in databases in tables qts_quotes

        Returns: None

        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (user_id) SELECT user_id FROM {1} WHERE telegram_id = %s"
            cursor.execute(sql.format(self._table_replacements, self._table_users), (telegram_id,))
            self.connection.commit()

    def get_subscription_status(self, telegram_id: Optional[int | str]) -> Optional[bool]:
        """
            Status subscription of user for send replacements

        Args:
            telegram_id: user id in telegram

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT `status` FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id = %s"

            cursor.execute(sql.format(self._table_replacements, self._table_users), (telegram_id,))
            return bool(*_unpack_all_values_with_dict(cursor))

    def get_subscription_send_method(self, telegram_id: Optional[int | str]) -> Optional[int]:
        """
            Send mode subscription of user for send replacements

        Args:
            telegram_id: user id in telegram

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT `send_method` FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id = %s"
            cursor.execute(sql)
            return int(*_unpack_all_values_with_dict(cursor))

    def get_subscription_status_and_send_method(self, telegram_id: Optional[int | str]) -> Optional[tuple]:
        """
            Send mode and status subscription of user for send replacements

        Args:
            telegram_id: user id in telegram

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT `send_method`, `status` FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id = %s"

            cursor.execute(sql.format(self._table_replacements, self._table_users), (telegram_id,))
            result: dict = dict(cursor.fetchone())
            return result.get('status', 1), result.get('send_method', 4)

    def update_subscription_status(self, telegram_id: Optional[int | str], status: Optional[bool | int]):
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING(`user_id`) SET `status`=%s WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_replacements, self._table_users), (status, telegram_id))
            self.connection.commit()

    def update_subscription_send_method(self, telegram_id: Optional[int | str],
                                        send_method: Optional[bool | int]):
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING(`user_id`) SET `send_method`=%s WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_replacements, self._table_users), (send_method, telegram_id))
            self.connection.commit()

    def __get_subscription_who_get_replacements(self, send_method: Optional[int]):
        if send_method not in (1, 2):
            return ValueError("send_mode not 1 or 2")

        with self.connection.cursor() as cursor:
            # пояснення до запиту:
            # якщо:
            # 1) хоче отримувати заміни
            # 2) він підписався на той тип чи інший тип замін або на всі
            # 3) або він підписався на щось перше і при цьому
            # 4) раніше заміни не приходили
            # 5) приходили сьогодні тільки того типу, що перше надійшло
            # 6) або заміни сьогодні ще не приходили, або ми не знаємо час надсилання

            sql = "SELECT {1}.telegram_id FROM {0} INNER JOIN {1} USING(`user_id`) " \
                  "WHERE {0}.status=1 AND " \
                  "( " \
                  "{0}.send_method IN (%s, 3) OR {0}.send_method=4 AND " \
                  "( " \
                  "{0}.last_time_of_get IS NULL OR {0}.last_send_method IS NULL " \
                  "OR {0}.last_time_of_get=CURDATE() AND {0}.last_send_method=%s " \
                  "OR NOT {0}.last_time_of_get=CURDATE()" \
                  ")" \
                  ")"
            cursor.execute(
                sql.format(self._table_replacements, self._table_users),
                (send_method, send_method)
            )
            return _unpack_all_values_with_dict(cursor)

    def get_subscription_who_get_photo(self):
        """
        All sub who get photo replacements
        """
        return self.__get_subscription_who_get_replacements(1)

    def get_subscription_who_get_replacements_from_site(self):
        """
        All sub who get photo replacements
        """
        return self.__get_subscription_who_get_replacements(2)

    def update_last_time_send_replacements(self, send_method: int):
        """

        @return:
        """

        # IF status=1 and send_method in (_send_method,3) and TODAY!=last_time_of_get and
        # _send_method in (last_send_mode, None)

        list_user = self.__get_subscription_who_get_replacements(send_method=send_method)
        if not len(list_user):
            return
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING(`user_id`) " \
                  "SET {0}.last_time_of_get=CURDATE(), {0}.last_send_method=%s " \
                  "WHERE {1}.telegram_id IN %s"  # переписати запит
            cursor.execute(sql.format(self._table_replacements, self._table_users), (send_method, list_user))
            self.connection.commit()

    def get_subscription_name_group(self, telegram_id: Optional[int | str]) -> Optional[str]:
        """
            Get name group in databases

        Args:
            telegram_id: user id in telegram

        Returns:
            '' or name_group

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.name_group FROM {0} INNER JOIN {1} USING(user_id) WHERE {1}.telegram_id = %s"

            cursor.execute(sql.format(self._table_replacements, self._table_users), (telegram_id,))
            cursor_fetchone = cursor.fetchone()
            if cursor_fetchone is None:
                return None
            result: dict = dict(cursor_fetchone)
            return result.get('name_group', None)

    def update_subscription_name_group(self, telegram_id: Optional[int | str], name_group: Optional[str]) -> None:
        """
            Update name group in databases for subscription

        Args:
            telegram_id: user id in telegram
            name_group: name group of user

        Returns:
            None
        """
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING(`user_id`) SET {0}.name_group=%s WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_replacements, self._table_users), (name_group, telegram_id))
            self.connection.commit()

    def insert_all_replacements_in_table(self, all_replacements: List[list[str, ...] | tuple[str, ...]]):
        """

        @param all_replacements:
        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (name_group, number_lesson, old_teacher, name_subject, new_teacher, room) " \
                  "VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.executemany(sql.format(self._table_for_table_replacements), all_replacements)
            self.connection.commit()

    def insert_news_replacements_in_table(self, news_of_replacements: List[list[str, ...] | tuple[str, ...] | str]):
        """

        @param news_of_replacements:
        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (news) " \
                  "VALUES (%s)"
            cursor.executemany(sql.format(self._table_for_news_replacements), news_of_replacements)
            self.connection.commit()

    def insert_info_replacements_in_table(self, info_of_replacements: List[list[str, ...] | tuple[str, ...]]):
        """

        @param info_of_replacements:
        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (info) " \
                  "VALUES (%s)"
            cursor.executemany(sql.format(self._table_for_info_replacements), info_of_replacements)
            self.connection.commit()

    def get_all_replacements_for_group_with_table(self, name_group: Optional[str]) -> List[list[str, ...]]:
        """

        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.number_lesson, {0}.name_subject, {0}.new_teacher, {0}.room FROM {0} " \
                  "WHERE {0}.name_group=%s"
            cursor.execute(sql.format(self._table_for_table_replacements), (name_group,))
            return _unpack_all_values_with_dict(cursor, new_support=True)

    def get_news_replacements_with_table(self) -> List[str]:
        """

        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.news FROM {0}"
            cursor.execute(sql.format(self._table_for_news_replacements))
            return _unpack_all_values_with_dict(cursor)

    def get_info_replacements_with_table(self) -> list:
        """

        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.info FROM {0}"
            cursor.execute(sql.format(self._table_for_info_replacements))
            return _unpack_all_values_with_dict(cursor)

    def clear_all_table_with_replacements(self):
        with self.connection.cursor() as cursor:
            sql = "TRUNCATE TABLE {0}"
            #sql = "DELETE FROM {0}"
            cursor.execute(sql.format(self._table_for_table_replacements))
            cursor.execute(sql.format(self._table_for_info_replacements))
            cursor.execute(sql.format(self._table_for_news_replacements))
            self.connection.commit()


class Schedule(BaseMysql):
    def clear_all_table_with_schedule(self):
        with self.connection.cursor() as cursor:
            sql = "TRUNCATE TABLE {0}"
            cursor.execute(sql.format(self._table_table_schedule))
            self.connection.commit()

    def insert_all_schedule_in_table(self, all_schedule: List[list[str, ...] | tuple[str, ...]]):
        """

        @param all_schedule:
        @return:
        """

        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (day, name_group, num_s, number, start_time, end_time, name, teacher, room) " \
                  "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.executemany(sql.format(self._table_table_schedule), all_schedule)
            self.connection.commit()

    def get_all_title_group_u(self) -> List[str]:
        with self.connection.cursor() as cursor:
            sql = "SELECT DISTINCT {0}.name_group FROM {0}"  # ORDER BY {0}.name_group DESC"
            cursor.execute(sql.format(self._table_table_schedule))
            return _unpack_all_values_with_dict(cursor)

    def get_first_letter_teacher(self) -> List[str]:
        with self.connection.cursor() as cursor:
            sql = ("CREATE TEMPORARY TABLE temp SELECT LEFT({0}.teacher, 1) AS first_letter FROM {0} " \
                   "WHERE {0}.teacher IS NOT null GROUP BY {0}.teacher; ",
                   'SELECT DISTINCT temp.first_letter FROM temp')
            cursor.execute(sql[0].format(self._table_table_schedule))
            cursor.execute(sql[1])
            return _unpack_all_values_with_dict(cursor)

    def get_teacher_from_first_letter(self, letter: str) -> List[str]:
        with self.connection.cursor() as cursor:
            sql = "SELECT DISTINCT {0}.teacher FROM {0} WHERE {0}.teacher LIKE '{letter}%'"
            cursor.execute(sql.format(self._table_table_schedule, letter=letter))
            return _unpack_all_values_with_dict(cursor)

    def get_information_of_user(self, teacher: str) -> json:
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.day, {0}.number, {0}.start_time, {0}.end_time, {0}.name_group, {0}.name, {0}.room " \
                  "FROM {0} WHERE {0}.teacher = %s"
            cursor.execute(sql.format(self._table_table_schedule), (teacher,))
            return cursor.fetchall()

    def get_information_of_group(self, name_group: str,  day:str) -> json:
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.number, {0}.num_s, {0}.start_time, {0}.end_time, {0}.name, {0}.teacher, {0}.room " \
                  "FROM {0} WHERE {0}.name_group = %s AND {0}.day = %s"
            cursor.execute(sql.format(self._table_table_schedule), (name_group, day))
            return cursor.fetchall()


class MediaFileID(BaseMysql):

    def _add(self, file_id: Optional[str]):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} ({0}.telegram_file_id) VALUES (%s)"
            cursor.execute(sql.format(self._table_files_id), (file_id,))
            self.connection.commit()

    def _exist(self, file_id: Optional[str]):
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {0} WHERE {0}.telegram_file_id = %s"
            return bool(cursor.execute(sql.format(self._table_files_id), (file_id,)))

    def _add_if_not_exist(self, file_id: Optional[str]):
        if not self._exist(file_id):
            self._add(file_id)

    def add(self, telegram_id: Optional[int | str], file_id: Optional[str], type_file_id: Optional[str]):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} ({0}.user_id, {0}.file_id, {0}.type)" \
                  "VALUES (" \
                  "(SELECT `user_id` FROM {1} WHERE {1}.telegram_id = %s), " \
                  "(SELECT `file_id` FROM {2} WHERE {2}.telegram_file_id = %s), " \
                  "%s)"

            self._add_if_not_exist(file_id)

            cursor.execute(
                sql.format(self._table_tmp_file_id, self._table_users, self._table_files_id),
                (telegram_id, file_id, type_file_id)
            )
            self.connection.commit()

    def delete(self, telegram_id: Optional[int | str], type_file_id: Optional[str] = None):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM `{0}` WHERE {0}.user_id = (" \
                  "SELECT {1}.user_id FROM {1} WHERE {1}.telegram_id= %s)"
            if type_file_id:
                sql += " AND {0}.type = %s"
            cursor.execute(sql.format(self._table_tmp_file_id, self._table_users), (telegram_id, type_file_id))
            self.connection.commit()

    def get(self, telegram_id: Optional[int | str], type_file_id: Optional[str] = None) -> Optional[list]:
        with self.connection.cursor() as cursor:
            sql = "SELECT {2}.telegram_file_id FROM {2} INNER JOIN {0} USING(`file_id`) INNER JOIN {1} " \
                  "USING(`user_id`) WHERE {1}.telegram_id = %s"
            if type_file_id:
                sql += " AND {0}.type=%s"
                cursor.execute(
                    sql.format(self._table_tmp_file_id, self._table_users, self._table_files_id),
                    (telegram_id, type_file_id)
                )
                return _unpack_all_values_with_dict(cursor)

            cursor.execute(
                sql.format(self._table_tmp_file_id, self._table_users, self._table_files_id),
                (telegram_id,)
            )
            return _unpack_all_values_with_dict(cursor)

    def exist(
            self,
            telegram_id: Optional[int | str],
            type_file_id: Optional[str],
            file_id: Optional[str] = None
    ) -> Optional[bool]:
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {2} INNER JOIN {0} USING(`file_id`) INNER JOIN {1} " \
                  "USING(`user_id`) WHERE {1}.telegram_id = %s AND {0}.type=%s"
            if file_id:
                sql += " AND {2}.telegram_file_id=%s"
                return bool(cursor.execute(
                    sql.format(self._table_tmp_file_id, self._table_users, self._table_files_id),
                    (telegram_id, type_file_id, file_id))
                )

            return bool(cursor.execute(
                sql.format(self._table_tmp_file_id, self._table_users, self._table_files_id),
                (telegram_id, type_file_id))
            )

    def add_file_id_in_replacements_from_tmp_file_id(
            self,
            message_id: Optional[int | str],
            telegram_id: Optional[int | str],
            type_file_id: Optional[str]
    ):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} ({0}.user_id, {0}.file_id, {0}.message_id) " \
                  "(" \
                  "SELECT {1}.user_id, {1}.file_id, %s FROM {1} INNER JOIN {2} USING (`user_id`) " \
                  "WHERE {2}.telegram_id = %s AND {1}.type=%s)"

            cursor.execute(
                sql.format(
                    self._table_file_id_replacements, self._table_tmp_file_id, self._table_users
                ),
                (message_id, telegram_id, type_file_id)
            )
            self.connection.commit()

    def delete_file_id_in_replacements(
            self,
            message_id: Optional[int | str]
    ):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM {0} WHERE {0}.message_id = %s"

            cursor.execute(
                sql.format(self._table_file_id_replacements),
                (message_id,)
            )
            self.connection.commit()

    def get_file_id_replacements(
            self,
            message_id: Optional[int | str]
    ):
        with self.connection.cursor() as cursor:
            sql = "SELECT {2}.telegram_file_id, {1}.username " \
                  "FROM {2} INNER JOIN {0} USING(`file_id`) INNER JOIN {1} " \
                  "USING(`user_id`) WHERE {0}.message_id = %s"
            cursor.execute(
                sql.format(
                    self._table_file_id_replacements, self._table_users, self._table_files_id
                ),
                (message_id,)
            )

            return _unpack_all_values_with_dict(cursor)


class GlobalValues(BaseMysql):

    def add(self, name: Optional[str], value: Optional[str]):
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0}({0}.name, {0}.value) VALUES (%s, %s)"
            cursor.execute(
                sql.format(self._table_global_settings), (name, value)
            )
            self.connection.commit()

    def update(self, name: Optional[str], value: Optional[str]):
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} SET {0}.value=%s WHERE {0}.name = %s"
            cursor.execute(
                sql.format(self._table_global_settings), (value, name)
            )
            self.connection.commit()

    def get(self, name: Optional[str]) -> Optional[str | None]:
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.value FROM {0} WHERE {0}.name = %s"
            cursor.execute(
                sql.format(self._table_global_settings), (name,)
            )
            lst = cursor.fetchall()
            if not lst:
                return None
            lst_value: dict = dict(lst[0])
            return lst_value.get(list(lst_value.keys())[0], '')

    def delete(self, name: Optional[str]):
        with self.connection.cursor() as cursor:
            sql = "DELETE FROM {0} WHERE {0}.name = %s"
            cursor.execute(
                sql.format(self._table_global_settings), (name,)
            )
            self.connection.commit()

    def exist(self, name: Optional[str]) -> Optional[bool]:
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {0} WHERE {0}.name = %s"

            return bool(cursor.execute(sql.format(
                self._table_global_settings), (name,))
            )


class AnonimChat(BaseMysql):

    def is_check_exist_user(
            self,
            telegram_id: Optional[int]
    ) -> Optional[bool]:
        """
        Checking user in databases of telegram_id

        Args:
            telegram_id: user id in telegram

        Returns:
            True/False - is existed/not is existed

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id=%s"

            return bool(cursor.execute(sql.format(self._table_anonim_users, self._table_users), (telegram_id,)))

    def add_new_user(
            self,
            telegram_id: Optional[int]
    ) -> Optional[None]:
        """
        INSERT new user in tables with anonim table in databases

        Args:


        Returns: None

        """
        with self.connection.cursor() as cursor:
            sql = "INSERT INTO {0} (user_id) SELECT user_id FROM {1} WHERE telegram_id=%s"

            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (telegram_id,))
            self.connection.commit()

    def update_sex_in_info_user(self, telegram_id: Optional[int | str], sex: Optional[bool | int]):
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING(`user_id`) SET `sex`=%s WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (sex, telegram_id))
            self.connection.commit()

    def update_show_username_in_info_user(self, telegram_id: Optional[int | str], show_username: Optional[bool | int]):
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING(`user_id`) SET `show_username`=%s WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (show_username, telegram_id))
            self.connection.commit()

    def get_sex_in_info_user(self, telegram_id: Optional[int | str]) -> Optional[bool]:
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.sex FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (telegram_id,))
            return _unpack_list(_unpack_all_values_with_dict(cursor), 0)

    def get_show_username_in_info_user(self, telegram_id: Optional[int | str]):
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.show_username FROM {0} INNER JOIN {1} USING(`user_id`) WHERE {1}.telegram_id=%s"
            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (telegram_id,))
            return _unpack_list(_unpack_all_values_with_dict(cursor), 0)

    def get_all_info_for_top_rating_users(self, limit=5):
        with self.connection.cursor() as cursor:
            sql = "SELECT {1}.username, {0}.count_message, {0}.show_username " \
                  "FROM {0} INNER JOIN {1} USING(`user_id`) " \
                  "WHERE {0}.count_message > 0 ORDER BY {0}.count_message DESC LIMIT %s"
            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (limit,))
            return _unpack_all_values_with_dict(cursor, key=True, new_support=True)

    def is_check_exist_in_queue(
            self,
            telegram_id: Optional[int]
    ) -> Optional[bool]:
        """
        Checking user in databases of telegram_id

        Args:
            telegram_id: user id in telegram

        Returns:
            True/False - is existed/not is existed

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM {0} INNER JOIN {1} USING(user_id) " \
                  "WHERE {0}.telegram_id=%s AND {1}.search_user_status=%s"

            return bool(cursor.execute(
                sql.format(self._table_users, self._table_anonim_users), (telegram_id, True)))

    def update_queue_status(
            self,
            telegram_id: Optional[int],
            status: Optional[bool]
    ) -> Optional[None]:
        """
        INSERT new user in tables with anonim_queue table in databases

        Args:


        Returns: None

        """
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING (user_id) SET search_user_status=%s " \
                  "WHERE {1}.telegram_id=%s"

            cursor.execute(sql.format(self._table_anonim_users, self._table_users),
                           (status, telegram_id))
            self.connection.commit()

    def get_count_user_in_queue(
            self,
    ) -> Optional[Any]:
        """
        Get count user in queue

        Args:
            @param sex:

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT sex, COUNT(*) FROM {0} WHERE search_user_status=%s " \
                  "GROUP BY sex HAVING sex IN (0,1) ORDER BY sex ASC "

            cursor.execute(sql.format(self._table_anonim_users), (True,))
            return _unpack_all_values_with_dict(cursor=cursor)

    def get_if_two_sex_user_in_queue(
            self,
    ) -> Optional[bool]:
        """
        Get count user in queue

        Args:
            @param sex:

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT sex FROM {0} WHERE search_user_status=%s GROUP BY sex"

            cursor.execute(sql.format(self._table_anonim_users), (True,))
            tmp = _unpack_all_values_with_dict(cursor=cursor)
            return len(tmp) >= 2

    def get_all_telegram_id_in_queue(
            self,
            sex: Optional[bool]
    ) -> Optional[set]:
        """
        Get count user in queue

        Args:
            @param sex:

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {1}.telegram_id " \
                  "FROM {0} INNER JOIN {1} USING (user_id) WHERE {0}.sex=%s AND {0}.search_user_status=%s"

            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (sex, True))
            return set(_unpack_all_values_with_dict(cursor=cursor))

    def update_connect_with(
            self,
            telegram_id: Optional[int | str],
            connect_with_telegram_id: Optional[int | str]
    ):
        """
        Update column connect_with for user_id

        @param telegram_id:
        @param connect_with_telegram_id:
        @return:
        """
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING (user_id) SET connect_with=(" \
                  "SELECT {1}.user_id FROM {1} WHERE {1}.telegram_id=%s" \
                  ") WHERE {1}.telegram_id=%s"

            cursor.execute(sql.format(self._table_anonim_users, self._table_users),
                           (connect_with_telegram_id, telegram_id))
            self.connection.commit()

    def get_telegram_id_with_connect(
            self,
            telegram_id: Optional[int]
    ) -> Any:
        """
        Get user_id with connect

        Args:
            @param telegram_id:

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.telegram_id FROM {0} WHERE user_id=(SELECT {1}.connect_with " \
                  "FROM {0} INNER JOIN {1} USING (user_id) WHERE {0}.telegram_id=%s)"

            cursor.execute(sql.format(self._table_users, self._table_anonim_users), (telegram_id,))
            return _unpack_list(_unpack_all_values_with_dict(cursor), 0)

    def is_check_exist_with_connect(
            self,
            telegram_id: Optional[int]
    ) -> Optional[int]:
        """
        Get user_id with connect

        Args:
            @param telegram_id:

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT {0}.connect_with FROM {0} INNER JOIN {1} USING(user_id) WHERE {1}.telegram_id=%s"

            cursor.execute(sql.format(self._table_anonim_users, self._table_users), (telegram_id,))
            return _unpack_list(_unpack_all_values_with_dict(cursor), 0)

    def get_count_with_connect(
            self,
    ) -> Any:
        """
        Get count all user in chat

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM {0} WHERE NOT {0}.connect_with=%s"

            cursor.execute(sql.format(self._table_anonim_users), (None,))
            return _unpack_list(_unpack_all_values_with_dict(cursor), 0)

    def get_count_in_queue(
            self,
    ) -> Any:
        """
        Get count all user in queue

        Returns:

        """
        with self.connection.cursor() as cursor:
            sql = "SELECT COUNT(*) FROM {0} WHERE NOT {0}.search_user_status=%s"
            cursor.execute(sql.format(self._table_anonim_users), (True,))
            return _unpack_all_values_with_dict(cursor=cursor)[0]

    def add_one_message_to_all_message(
            self,
            telegram_id: Optional[int]
    ):
        with self.connection.cursor() as cursor:
            sql = "UPDATE {0} INNER JOIN {1} USING (user_id) SET {0}.count_message={0}.count_message + 1 " \
                  "WHERE {1}.telegram_id=%s"

            cursor.execute(sql.format(self._table_anonim_users, self._table_users),
                           (telegram_id,))
            self.connection.commit()


class Holy(BaseMysql):
    def select_text(self, date: datetime.date):
        with self.connection.cursor() as cursor:
            day = date.day
            month = date.month
            year = date.year

            sql = 'SELECT {0}.text FROM {0} WHERE MONTH({0}.date)=MONTH(%s) AND DAY({0}.date)=DAY(%s)'

            cursor.execute(
                sql.format(self._table_holy_text), (
                    datetime.date(day=day, month=month, year=year), datetime.date(day=day, month=month, year=year)
                )
            )
            return _unpack_list(_unpack_all_values_with_dict(cursor), 0)
