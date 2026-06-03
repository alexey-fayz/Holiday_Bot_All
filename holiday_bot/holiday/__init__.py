"""
Модуль для работы с праздниками
"""
from .config import AppConfig, APIConfig, DatabaseConfig, LoggingConfig, get_default_config
from .custom_holiday import MyHolidays
from .handler import HolidayHandler, fetch_holidays_from_api

__all__ = [
    'AppConfig',
    'APIConfig',
    'DatabaseConfig',
    'LoggingConfig',
    'get_default_config',
    'MyHolidays',
    'HolidayHandler',
    'fetch_holidays_from_api'  # ← Добавляем экспорт функции
]