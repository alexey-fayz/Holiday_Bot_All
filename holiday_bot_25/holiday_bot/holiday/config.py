from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class APIConfig:
    """Конфигурация для API запросов"""
    base_url: str = "https://date.nager.at/api/v3"  # Убедимся, что нет лишнего пути
    timeout: int = 10
    retry: int = 3

@dataclass(frozen=True)
class DatabaseConfig:
    """Конфигурация для работы с базой данных"""
    file_path: str = "custom_holiday.json"
    encoding: str = "utf-8"

@dataclass(frozen=True)
class LoggingConfig:
    """Конфигурация для логирования"""
    level: str = "WARNING"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

@dataclass(frozen=True)
class AppConfig:
    """Основной конфигурационный класс"""
    api: APIConfig = field(default_factory=APIConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

def get_default_config() -> AppConfig:
    """Создает и возвращает конфигурацию по умолчанию"""
    return AppConfig()