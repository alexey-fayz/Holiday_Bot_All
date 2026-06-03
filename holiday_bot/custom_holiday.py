from datetime import datetime, date
from pathlib import Path

from holidays.countries.russia import Russia
import json
from typing import Dict, List, Tuple


# TODO: Задача 6.7 - Реализовать Mixin для подсчета вызовов методов
class CallCounterMixin:
    """Миксин для подсчета количества вызовов методов"""

    def __init__(self):
        # Словарь для хранения счетчиков вызовов методов
        self._call_counts = {}

    def _increment_call_count(self, method_name: str):
        """Увеличивает счетчик вызовов указанного метода"""
        if method_name not in self._call_counts:
            self._call_counts[method_name] = 0
        self._call_counts[method_name] += 1

    def get_call_count(self, method_name: str) -> int:
        """Возвращает количество вызовов указанного метода"""
        return self._call_counts.get(method_name, 0)


class MyHolidays(CallCounterMixin, Russia):  # TODO: Задача 6.7 - Добавить наследование от CallCounterMixin
    """Класс для кастомных праздников с наследованием от Russia"""

    total_holidays_loaded = 0

    def __init__(self, **kwargs):
        # Инициализация миксина
        CallCounterMixin.__init__(self)

        # Инициализация базового класса Russia
        super().__init__(**kwargs)

        self.loaded_count = 0
        self.custom_holidays = self._load_custom_holidays()
    
    @staticmethod
    def _parse_date_string(date_string: str) -> date:
        """Парсинг строки даты в объект date"""
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    
    @classmethod
    def get_total_holidays_count(cls):
        """Получение общего количества загруженных праздников"""
        return cls.total_holidays_loaded

    def _load_custom_holidays(self) -> Dict[date, List[str]]:
        """Загрузка кастомных праздников из базы данных"""
        # Считаем вызов метода
        self._increment_call_count('_load_custom_holidays')

        try:
            customholidays_file = Path(__file__).parent / "custom_holiday.json"
            custom_hols = {}
            with open(customholidays_file, encoding="utf-8") as f:
                for holiday, name in json.load(f).items():
                    holiday_date = datetime.strptime(holiday, '%Y-%m-%d').date()
                    if holiday_date in custom_hols:
                        custom_hols[holiday_date].append(name)
                    else:
                        custom_hols[holiday_date] = [name]
                
                # Обновляем счетчик для объекта
                self.loaded_count = len(custom_hols)
                
                # Обновляем счетчик класса
                MyHolidays.total_holidays_loaded += len(custom_hols)
                
                return custom_hols
        except Exception:
            return {}

    def get_list(self, date_obj: date) -> Tuple[List[str], List[str]]:
        """Получение раздельных списков официальных и кастомных праздников"""
        official_holidays = super().get(date_obj, [])
        if isinstance(official_holidays, str):
            official_holidays = [official_holidays]
        else:
            official_holidays = list(official_holidays)

        custom_holidays: List[str] = []
        for holiday_date, names in self.custom_holidays.items():
            if (holiday_date.month, holiday_date.day) == (date_obj.month, date_obj.day):
                custom_holidays.extend(names)

        return official_holidays, custom_holidays

    def get_loaded_count(self) -> int:
        """Получение количества загруженных праздников для данного объекта"""
        return self.loaded_count
    
    @property
    def custom_holidays_count(self) -> int:
        """Получение количества кастомных праздников через property"""
        return len(self.custom_holidays)
