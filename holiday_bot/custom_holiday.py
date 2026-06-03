from datetime import datetime, date
from pathlib import Path

from holidays.countries.russia import Russia
import json
from typing import Dict, List, Tuple


class MyHolidays(Russia):
    """Класс для кастомных праздников с наследованием от Russia"""

    def __init__(self, **kwargs):
        """Инициализация класса с загрузкой кастомных праздников"""
        # Устанавливаем язык по умолчанию на русский
        if 'language' not in kwargs:
            kwargs['language'] = 'ru'
        super().__init__(**kwargs)
        self.custom_holidays = self._load_custom_holidays()

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
                
                return custom_hols
        except Exception as e:
            return {}

    def get_list(self, date_obj: date) -> Tuple[List[str], List[str]]:
        """Получение раздельных списков официальных и кастомных праздников"""
        # Получаем официальные праздники из родительского класса
        official_result = super().get(date_obj, [])
        
        # Преобразуем официальные праздники в список
        official = []
        if official_result:
            if isinstance(official_result, list):
                official.extend(official_result)
            else:
                official.append(str(official_result))
        
        # Получаем кастомные праздники, игнорируя год
        custom = []
        for holiday_date, holiday_names in self.custom_holidays.items():
            # Сравниваем только месяц и день, игнорируя год
            if holiday_date.month == date_obj.month and holiday_date.day == date_obj.day:
                if isinstance(holiday_names, list):
                    custom.extend(holiday_names)
                else:
                    custom.append(str(holiday_names))
        
        return official, custom