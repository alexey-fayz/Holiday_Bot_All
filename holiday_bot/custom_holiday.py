from datetime import datetime, date
from pathlib import Path

from holidays.countries.russia import Russia
import json
from typing import Dict, List, Tuple


class CallCounterMixin:
    """Миксин для подсчета количества вызовов методов"""
    
    def __init__(self, **kwargs):
        self._call_counts = {}
        super().__init__(**kwargs)
    
    def _increment_call_count(self, method_name: str):
        """Увеличение счетчика вызовов для указанного метода"""
        if method_name not in self._call_counts:
            self._call_counts[method_name] = 0
        self._call_counts[method_name] += 1
    
    def get_call_count(self, method_name: str) -> int:
        """Получение количества вызовов метода"""
        return self._call_counts.get(method_name, 0)


class MyHolidays(CallCounterMixin, Russia):
    """Класс для кастомных праздников с наследованием от Russia"""

    total_holidays_loaded = 0

    def __init__(self, **kwargs):
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
            if self._compare_dates_without_year(holiday_date, date_obj):
                custom_holidays.extend(names)

        return official_holidays, custom_holidays

    def _compare_dates_without_year(self, date1: date, date2: date) -> bool:
        """Приватный метод для сравнения дат без учета года"""
        return (date1.month, date1.day) == (date2.month, date2.day)

    def get(self, date_obj: date, default=None):
        """Получение списка праздников для даты"""
        dt = [
            dt for dt in self.custom_holidays.keys()
            if self._compare_dates_without_year(dt, date_obj)
        ]
        dt = dt[0] if dt else date_obj
        custom_holidays = self.custom_holidays.get(dt, [])
        official_holidays = super().get(date_obj, [])

        all_holidays = f'{official_holidays} {" ,".join(custom_holidays)}'
        return all_holidays if all_holidays else default

    def get_list(self, date_obj: date):
        """Получение раздельных списков официальных и кастомных праздников"""
        official_holidays = super().get(date_obj, [])
        
        custom_holidays = []
        for dt, holidays in self.custom_holidays.items():
            if self._compare_dates_without_year(dt, date_obj):
                custom_holidays.extend(holidays)
        
        return (official_holidays, custom_holidays)

    def get_loaded_count(self) -> int:
        """Получение количества загруженных праздников для данного объекта"""
        return self.loaded_count
    
    @property
    def custom_holidays_count(self) -> int:
        """Получение количества кастомных праздников через property"""
        return len(self.custom_holidays)

    # ✅ Задача 6.9 — Магический метод __str__
    def __str__(self) -> str:
        """Человекочитаемое строковое представление объекта"""
        return f"MyHolidays: {self.custom_holidays_count} custom holidays loaded"
