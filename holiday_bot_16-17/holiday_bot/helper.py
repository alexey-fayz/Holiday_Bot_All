from datetime import date
from typing import Tuple

from holidays.countries import Russia

CUSTOM_HOLIDAYS = {
    date(2023, 1, 1): ["День кота"],
    date(2024, 1, 1): ["День кофе"],
    date(2024, 11, 4): ["День геймера в лото"],
}


def get(custom_holidays: dict, date_obj: date, default=None):
    """Получение списка праздников для даты"""
    # custom = []
    # for dt in custom_holidays.keys():
    #     if (dt.month, dt.day) == (date_obj.month, date_obj.day):
    #         custom.extend(custom_holidays.get(dt, []))    official_holidays = Russia().get(date_obj, [])
    all_holidays = f'{official_holidays} {" ,".join(custom)}'
    return all_holidays if (custom or official_holidays) else default


def get_list(custom_holidays: dict, date_obj: date) -> Tuple[list[str], list[str]]:
    """Получение раздельных списков официальных и кастомных праздников"""
    official = Russia().get(date_obj, [])
    # custom = []
    # for dt in custom_holidays.keys():
    #     if (dt.month, dt.day) == (date_obj.month, date_obj.day):
    #         custom.extend(custom_holidays.get(dt, []))
    return official, custom


def get_custom_holidays_on_day_of_month(date_check: date, custom_holidays: dict) -> list[str] or list[None]:
    pass