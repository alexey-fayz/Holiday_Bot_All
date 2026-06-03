import logging
from datetime import datetime, date
from functools import wraps
from pathlib import Path

from holidays.countries.russia import Russia
import json
from typing import Dict, List, Tuple

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)
logger = logging.getLogger(__name__)


def log_exceptions(func):
    """Декоратор для логирования вызова и ошибок"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__qualname__
        logger.info(f"→ Вызов: {func_name} args={args[1:]}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"✓ Успешно: {func_name}")
            return result
        except Exception as e:
            logger.exception(f"✗ Ошибка в {func_name}: {e}")
            raise
    return wrapper


class MyHolidays(Russia):
    """Класс для кастомных праздников с наследованием от Russia"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.custom_holidays = self._load_custom_holidays()
    @log_exceptions
    def _load_custom_holidays(self) -> Dict[date, List[str]]:
        """Загрузка кастомных праздников из базы данных"""
        # Тут нужно добавить обработку исключения для чтения файла при его отсутсвии или неправильном пути
        customholidays_file = Path(__file__).parent / "custom_holiday.json"
        custom_hols = {}
        with open(customholidays_file, encoding="utf-8") as f:
            for holiday, name in json.load(f).items():
                holiday_date = datetime.strptime(holiday, '%Y-%m-%d').date()
                if holiday_date in custom_hols:
                    custom_hols[holiday_date].append(name)
                else:
                    custom_hols[holiday_date] = [name]
            return custom_hols
        

    @log_exceptions
    def get(self, date_obj: date, default=None):
        """Получение списка праздников для даты"""
        # compare_without year можно в функцию
        dt = [dt for dt in self.custom_holidays.keys() if (dt.month, dt.day) == (date_obj.month, date_obj.day)]
        dt = dt[0] if dt else date_obj
        custom_holidays = self.custom_holidays.get(dt, [])
        official_holidays = super().get(date_obj, [])

        all_holidays = f'{official_holidays} {" ,".join(custom_holidays)}'
        return all_holidays if all_holidays else default

    @log_exceptions
    def get_list(self, date_obj: date) -> Tuple[List[str], List[str]]:
        """Получение раздельных списков официальных и кастомных праздников"""
        official = super().get(date_obj, [])
        dt = [dt for dt in self.custom_holidays.keys() if (dt.month, dt.day) == (date_obj.month, date_obj.day)]
        dt = dt[0] if dt else date_obj
        custom = self.custom_holidays.get(dt, [])
        return official, custom

    @log_exceptions
    def get_closest_official_holiday(self):
        """Получение ближайшего официального праздника"""
        official = super().get_closest_holiday(datetime.now())
        return official
