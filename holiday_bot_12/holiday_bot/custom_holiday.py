import logging
from datetime import datetime, date
from pathlib import Path

from holidays.countries.russia import Russia
import json
from typing import Dict, List, Tuple


class MyHolidays(Russia):
    """Класс для кастомных праздников с наследованием от Russia"""
    
    # Атрибут класса - общий для всех объектов класса
    total_holidays_loaded = 0

    def __init__(self, **kwargs):
        """Инициализация класса с загрузкой кастомных праздников"""
        # Инициализируем счетчик ДО загрузки праздников
        self.loaded_count = 0
        
        # Инициализируем родительский класс
        super().__init__(**kwargs)
        
        # Загружаем кастомные праздники
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
                
                # Обновляем счетчик объекта на основе количества загруженных дат
                self.loaded_count = len(custom_hols)
                
                # Обновляем атрибут класса - общее количество для всех объектов
                MyHolidays.total_holidays_loaded += len(custom_hols)
                
                return custom_hols
        except Exception as e:
            # В случае ошибки оставляем loaded_count = 0
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

    @classmethod
    def get_total_holidays_count(cls) -> int:
        """Получение общего количества загруженных праздников через все объекты"""
        return cls.total_holidays_loaded


# Пример использования
if __name__ == "__main__":
    # Создаем первый объект
    obj1 = MyHolidays()
    print(f"Первый объект загрузил: {obj1.loaded_count} праздников")
    print(f"Общее количество: {MyHolidays.get_total_holidays_count()}")
    print(f"Атрибут класса через obj1: {obj1.total_holidays_loaded}")
    print(f"Атрибут класса через класс: {MyHolidays.total_holidays_loaded}")
    
    # Создаем второй объект
    obj2 = MyHolidays()
    print(f"\nВторой объект загрузил: {obj2.loaded_count} праздников")
    print(f"Общее количество: {MyHolidays.get_total_holidays_count()}")
    print(f"Атрибут класса через obj2: {obj2.total_holidays_loaded}")
    
    # Проверяем, что атрибуты объектов уникальны
    print(f"\nПроверка уникальности атрибутов объекта:")
    print(f"obj1.loaded_count: {obj1.loaded_count}")
    print(f"obj2.loaded_count: {obj2.loaded_count}")
    print(f"obj1.loaded_count == obj2.loaded_count: {obj1.loaded_count == obj2.loaded_count}")
    
    # Проверяем, что атрибут класса общий
    print(f"\nПроверка атрибута класса:")
    print(f"obj1.total_holidays_loaded == obj2.total_holidays_loaded: {obj1.total_holidays_loaded == obj2.total_holidays_loaded}")
    print(f"obj1.total_holidays_loaded == MyHolidays.total_holidays_loaded: {obj1.total_holidays_loaded == MyHolidays.total_holidays_loaded}")
    
    # Используем метод класса
    print(f"\nИспользование метода класса:")
    print(f"MyHolidays.get_total_holidays_count(): {MyHolidays.get_total_holidays_count()}")
    print(f"obj1.get_total_holidays_count(): {obj1.get_total_holidays_count()}")
    print(f"obj2.get_total_holidays_count(): {obj2.get_total_holidays_count()}")