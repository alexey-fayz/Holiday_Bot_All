from dataclasses import dataclass, field


@dataclass()
class APIConfig:
    base_url: str = "https://date.nager.at/api/v3/publicholidays"
    timeout: int = 10
    max_retries: int = 3


@dataclass(frozen=True)
class DatabaseConfig:
    file_path: str = "custom_holiday.json"
    encoding: str = "utf-8"


@dataclass(frozen=True)
class LoggingConfig:
    level: str = "WARNING"
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


@dataclass(frozen=True)
class AppConfig:
    api: APIConfig = field(default_factory=APIConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)


def get_default_config() -> AppConfig:
    return AppConfig()
