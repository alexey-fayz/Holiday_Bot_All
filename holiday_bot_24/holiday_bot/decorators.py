import logging
from functools import wraps
from typing import Any, Callable

# Импортируем конфиг
try:
    from holiday_bot.holiday.config import get_default_config
except ImportError:
    # Альтернативный импорт для разных случаев
    try:
        from .holiday.config import get_default_config
    except ImportError:
        # Создаем заглушку если ничего не работает
        def get_default_config():
            class DummyConfig:
                class logging:
                    level = "INFO"
            return DummyConfig()

def log_exceptions(func: Callable) -> Callable:
    """Декоратор для логирования исключений"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Получаем конфигурацию для логирования
        config = get_default_config()
        logger = logging.getLogger(func.__module__)
        
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка в {func.__name__}: {e}", exc_info=True)
            raise
    
    return wrapper