import json
import re
from time import perf_counter
from typing import List

import pandas
from loguru import logger
from openpyxl import Workbook
from openpyxl.cell import ReadOnlyCell
from openpyxl.reader.excel import load_workbook
from openpyxl.worksheet._read_only import ReadOnlyWorksheet
from pandas import ExcelFile

from utils.module.MyType import LinkedList
from utils.mysql import Schedule
from utils.tools import abc


def is_null_column(value: dict.items) -> bool:
    """
    Check on entry column in json object

    @param value:
    @return:
    """

    def is_null_or_space(_value: str):
        if isinstance(_value, str | None):
            return _value is None or _value.isspace()
        return False

    if not value:
        return False
    unpack_dict = value[-1].values()
    return not len(unpack_dict) == len(tuple(filter(is_null_or_space, unpack_dict)))


def get_id_colum_with_bold_style(path_to_file) -> List[list]:
    """
    Get schema with bold

    @return:
    """

    wb: Workbook = load_workbook(path_to_file, read_only=True)
    begin = perf_counter()
    schema = list()
    for sheet in wb.worksheets:
        # переходимо по сторінках
        sheet: ReadOnlyWorksheet
        schema.append(list())
        for row in sheet:
            row = list(row)
            row: list[ReadOnlyCell]
            if not schema[-1]:  # якщо в нас перший прохід, то додаємо відповідну кількість стовпчиків у вигляді масиву
                schema[-1].extend([list() for _ in range(len(row))])
            while row:
                value = row.pop()
                schema[-1][len(row)].append(value.font.bold if value.font else False)
    end = perf_counter()
    # logger.debug("Total time {0:.2f}s".format(end - begin))
    return schema


class ReadExcelFile:

    def __init__(self, xls_file: ExcelFile, rows_with_name_group: int = 7, size_column: int = 81):
        self.COUNT_OF_COLUMN: int = 0
        self.COUNT_OF_ROW: int = 0
        self.excel_data_df = None

        self.xls_file = xls_file
        self.ROWS_WITH_NAME_GROUP = rows_with_name_group
        self.size_column = size_column

    def get_json(self, sheet_name: int = 0) -> dict[str]:
        self.excel_data_df = pandas.read_excel(
            self.xls_file, sheet_name=sheet_name, skiprows=self.ROWS_WITH_NAME_GROUP - 2
        )
        self.COUNT_OF_ROW, self.COUNT_OF_COLUMN = self.excel_data_df.shape

        self.excel_data_df.columns = range(self.COUNT_OF_COLUMN)
        # конвертуємо в зручний формат
        excel_data_df_with_convert = self.excel_data_df.convert_dtypes()

        # конвертуємо в json формат для зручного форматування
        excel_data_df_with_convert_by_js: dict = json.loads(
            excel_data_df_with_convert.to_json(orient='columns')
        )

        # фільтруємо запити, щоб зменшити обсяг роботи
        excel_data_df_with_convert_clean = dict(filter(is_null_column, excel_data_df_with_convert_by_js.items()))

        # конвертуємо у зрозумілий формат
        return json.loads(json.dumps(
            excel_data_df_with_convert_clean, indent=4, ensure_ascii=False)
        )


def get_json_of_time_lesson(
        day_column_k: str, number_lesson_column_k: str, oclock_column_k: str, page_of_json: dict
):
    """
    Формує json структуру годин пар

    @param day_column_k: назва дня
    @param number_lesson_column_k:
    @param oclock_column_k: години пар
    @param page_of_json: json object
    @return:
    """

    json_column: dict = page_of_json.get(day_column_k)
    json_column_k = LinkedList(json_column.keys())

    day = ''

    list_schema = dict()
    for key in json_column_k:
        if page_of_json[day_column_k][key]:
            day = page_of_json[day_column_k][key]

        if page_of_json[number_lesson_column_k][key]:
            number_lesson = page_of_json[number_lesson_column_k].get(key)
            __next_key = json_column_k.next(key)
            start_time = page_of_json[oclock_column_k].get(__next_key)
            end_time = page_of_json[oclock_column_k].get(json_column_k.next(__next_key))
            index = key
            list_schema[index] = {
                'day': day,
                'number': number_lesson,
                'start_time': start_time,
                'end_time': end_time,
            }
    return list_schema


def get_room_from_title(title_group: str) -> tuple[str, str]:
    # отримуємо всі основі значення
    name_group = ''
    tmp_room = re.findall(r'(?!-$)(\d{3}\S?)', title_group)
    # tmp_room = re.findall(r'(?!-$)([0-9]{3}[A-Za-zІА-Яа-яі]?)', title_group)
    tmp_group = re.findall(r'\D{2,3}-\d{3}\S?', title_group)
    # tmp_group = re.findall(r'[A-Za-zІА-Яа-яі]{2,3}-[0-9]{3}[A-Za-zІА-Яа-яі]?', title_group)

    if tmp_group:
        name_group = tmp_group[0]
    if len(tmp_room) - 1:
        return name_group, tmp_room[-1]
    return name_group, ''


def unzip_teacher(orig_value: str) -> tuple[str, str | None, str | None, str | None]:
    # Призвіще на одному рядку, аудиторія на наступному
    # Призвіще на 1-му стовпчику, друге призвіще на другому стовпчику

    # Об'єднати призвіща до одного формату. !
    is_num_e = lambda _value: re.search(r'\d', _value)
    is_num_e_n = lambda _value: not re.search(r'\d', _value)

    if orig_value is None:
        # якщо предмет вказаний казаний, а викладач - ні
        return '', None, None, None

    def replace_s(_value):
        _value = re.sub(r',', '.', _value)
        _value = re.sub(r'\s', '', _value)
        # _value = re.sub(r'(?=\w\.\w)', ' ', _value)
        _value = re.sub(r'(?<=\w)(?=\w\.)', ' ', _value)
        # _value = re.sub(r'(?<=\D)(?=\d)', ' ', _value)
        # _value = re.sub(r'(?<=\d{3}.)(?=[A-Z,А-Я])', ' ', _value)
        _value = re.sub(r'(?<=\d)(?=[A-Z,А-Я])', '/', _value)  # після цифрами

        _value = re.sub(r'(?<=\w\.)(?=\w\w+)', '/', _value)  # перед цифрами
        _value = re.sub(r'(?<=[a-z,а-я])(?=[A-Z,А-Я])', '/', _value)  # між словами

        return _value

    def replace_c(_value):
        _value = re.sub(r',', '.', _value)
        _value = re.sub(r'\s', '', _value)

        # для коректної роботи алгоритму
        _value = re.sub(r'\.(?=\w\.\w\.)', '', _value)

        # видаляємо першу частину з малої літери
        result = re.search(r'[IІА-Я]', _value)
        if result and not result.start() == 0:
            _value = _value[result.start():]

        _value = re.sub(r'(?<=\w)(?=\w\.)', ' ', _value)
        _value = re.sub(r'(?<=\w\.)(?=\w\w+)', '/', _value)  # перед цифрами
        _value = re.sub(r'(?<=\d)(?=[A-Z,А-Я])', '/', _value)  # після цифр
        _value = re.sub(r'(?<=[a-z,а-я])(?=[A-Z,А-Я])', '/', _value)  # між словами

        return _value

    value = replace_c(orig_value)

    # list_value: list[str] = re.split(r'\s*/\s*|\D+\D\d\d+', value)  # розбиваємо по "/"
    list_value: list[str] = re.split(r'/', value)  # розбиваємо по "/"

    if len(list_value) == 1 and is_num_e_n(list_value[0]):
        return list_value[0], None, None, None  # якщо в нас тільки одне значення, то виходимо

    elif len(list_value) == 2 and is_num_e_n(list_value[0]) and is_num_e_n(list_value[1]):  # Text, Text, None, None
        return list_value[0], list_value[1], None, None

    elif len(list_value) == 2 and is_num_e_n(list_value[0]) and is_num_e(list_value[1]):  # Text, None, Num None
        return list_value[0], None, list_value[1], None

    elif len(list_value) == 3 and is_num_e_n(list_value[0]) and is_num_e_n(list_value[1]) and \
            is_num_e(list_value[2]):
        # Text, Text, Num, None
        return list_value[0], list_value[1], list_value[2], None

    elif len(list_value) == 4 and is_num_e_n(list_value[0]) and is_num_e_n(list_value[1]) and \
            is_num_e(list_value[2]) and is_num_e(list_value[3]):
        return list_value[0], list_value[1], list_value[2], list_value[3]

    # another format
    elif len(list_value) == 3 and is_num_e_n(list_value[0]) and is_num_e(list_value[1]) and \
            is_num_e_n(list_value[2]):
        # Text, Num, Text, None
        return list_value[0], list_value[2], list_value[1], None

    return list_value[0], list_value[2], list_value[1], list_value[3]


def unzip_room(value: str | int | None) -> tuple[str | None, str | None]:
    if value is None:
        return None, None
    if isinstance(value, int):
        value = str(value)
    list_value: list[str] = re.split(r'\s*/\s*', value.strip())  # розбиваємо по "/" та символу пропуску

    if len(list_value) == 1:
        return list_value[0], None

    return list_value[0], list_value[1]


def get_room(room_from_title, value, value_1):
    room = None
    if value_1:
        room = value_1
    if room is None and value:
        room = value
    if room is None:
        room = room_from_title
    return room


def save_line(column_json, key_column_str, json_table_k, key, page_of_json, room_from_title):
    teacher = column_json.get(key_column_str)  # отримуємо назву викладача

    __key = json_table_k.next(key)  # отримуємо ключ наступного стовпця
    room = None
    if __key is not None:
        room = page_of_json[str(__key)].get(key_column_str)  # отримуємо номер групи

    teacher_1, teacher_2, room_1, room_2 = unzip_teacher(
        teacher)  # якщо комірка має додаткову інформацію
    room_1_1, room_1_2 = unzip_room(room)

    room = get_room(room_from_title, room_1, room_1_1)

    if teacher_1:
        teacher = teacher_1

    return teacher, room, teacher_2, room_2, room_1_2


def read_excel(path_to_file):
    begin = perf_counter()
    # unzip_teacher('Ілаш Н.Б. Мельник В.В.')
    # unzip_teacher('к.фізико-матем.н.Ілаш Н.Б.')
    # print(unzip_teacher('Студницька Л.М.           243а'))

    excel_file = ReadExcelFile(ExcelFile(path_to_file))

    bold_schema = get_id_colum_with_bold_style(path_to_file)  # отримуємо поля, в яких жирний текст

    result_structure: list[tuple] = []
    name_lesson = None
    lesson_schema_k = 0
    day = None
    num_s = None
    number = None
    start_time = None
    end_time = None

    flag = False
    tmp_name_teacher_flag = None

    sheet_tag = ""
    key_tag = ""
    key_column_tag = ""

    try:
        for sheet in range(len(excel_file.xls_file.sheet_names)):  # проходимося по кожній сторінці
            sheet_tag = sheet
            page_of_json = excel_file.get_json(sheet)

            day_column_k, number_lesson_column_k, oclock_column_k, *json_table_k = page_of_json.keys()
            # отримуємо перші три колонки дня, номерів пар, годин, та самі основні пари

            lesson_schema = get_json_of_time_lesson(day_column_k, number_lesson_column_k, oclock_column_k, page_of_json)

            json_table_k: LinkedList[int] = LinkedList(
                map(int, list(json_table_k))
            )  # конвертуємо в інший тип, для можливості отримання наступного елементу. Зберігає заповнені стовпчики
            for key in json_table_k:  # key column in tables
                key_tag = key

                column_json: dict[str] = page_of_json.get(str(key))  # отримуємо json з колонкою розкладу, для аналізу
                if column_json is None:  # якщо у нас такого ключа немає у списку, пропускаємо даний ключ key
                    continue
                json_column_k: LinkedList[int] = LinkedList(
                    map(int, list(column_json.keys())))  # отримуємо ключі колонки

                name_group = column_json.get(str(json_column_k.pop(0)))  # отримуємо назву груп
                if name_group is None:  # якщо назва групи не отримана, то пропускаємо дану колонку
                    continue

                name_group, room_from_title = get_room_from_title(name_group)

                for key_column in json_column_k:  # проходимося по кожному рядку в колонці
                    key_column_tag = key_column
                    key_column_str = str(key_column)

                    # if str(key_column_str) == "12" and str(sheet_tag) == str(4):
                    #    pass

                    if key_column_str in lesson_schema.keys():  # отримуємо інформацію про години пар
                        lesson_schema_k = int(key_column_str)

                        day = lesson_schema[key_column_str].get('day')  # назва дня
                        number = lesson_schema[key_column_str].get('number')  # номер пари
                        start_time = lesson_schema[key_column_str].get('start_time')
                        end_time = lesson_schema[key_column_str].get('end_time')

                    if key_column >= excel_file.size_column:
                        break  # якщо ми дійшли до кінця сторінки

                    if column_json.get(key_column_str) is None or column_json.get(key_column_str).isspace():
                        if flag or tmp_name_teacher_flag is not None:  # False
                            continue
                        else:
                            flag = True

                    if bold_schema[sheet][key][excel_file.ROWS_WITH_NAME_GROUP - 1 + key_column]:
                        # перевіряємо, чи колонка має текст із жирним стилем(предмет)
                        name_lesson = column_json.get(key_column_str)
                        # num_s: bool = not key_column - lesson_schema_k > 1

                        num_s = False
                        if key_column - lesson_schema_k == 1:
                            num_s = None
                        elif key_column == lesson_schema_k:
                            num_s = True

                        flag = False
                        tmp_name_teacher_flag = None
                        continue

                    teacher, room, teacher_2, room_2, room_1_2 = save_line(
                        column_json=column_json, key_column_str=key_column_str, json_table_k=json_table_k,
                        key=key, page_of_json=page_of_json, room_from_title=room_from_title
                    )

                    result_structure.append(
                        (day, name_group, num_s, number, start_time, end_time, name_lesson, teacher, room)
                    )

                    if teacher_2:
                        teacher = teacher_2
                        room = get_room(room_from_title, room_2, room_1_2)
                        result_structure.append(
                            (day, name_group, num_s, number, start_time, end_time, name_lesson, teacher, room)
                        )
                    tmp_name_teacher_flag = teacher
        end = perf_counter()
        logger.debug("Total time {0:.2f}s".format(end - begin))


    except Exception as e:
        msg = "Sheet - {0}, column - {1}({2}), line - {3}({4})".format(
            int(sheet_tag + 1), key_tag + 1, abc(key_tag + 1), key_column_tag, key_column_tag + 6)
        logger.warning("See coordinate on : {0}".format(msg))
        logger.warning("Error :{0}".format(e))
        return msg

    save_new_schedule_in_db(result_structure)



def save_new_schedule_in_db(result_structure: list[tuple[str, ...]]):
    Schedule().clear_all_table_with_schedule()

    logger.info("Saving schedule in db - {}".format(bool(result_structure)))
    Schedule().insert_all_schedule_in_table(result_structure)
