import logging
from typing import Optional, Dict, Any, List
import asyncio

# Импортируем aiohttp если есть
try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

# Импорты из того же пакета
from .config import AppConfig, get_default_config

class HolidayHandler:
    """Обработчик запросов к API праздников"""
    
    def __init__(self, config: AppConfig = None):
        self.config = config or get_default_config()
        self.logger = logging.getLogger(__name__)
    
    async def fetch_holidays_from_api(self, year: int, country_code: str) -> List[Dict[str, Any]]:
        """
        Асинхронный метод для получения праздников из API Nager.Date
        Возвращает список праздников или пустой список в случае ошибки
        """
        # Формируем правильный URL
        url = f"{self.config.api.base_url.rstrip('/')}/PublicHolidays/{year}/{country_code}"
        
        self.logger.debug(f"Запрос к URL: {url}")
        
        # Если aiohttp не установлен, возвращаем пустой список
        if not HAS_AIOHTTP:
            self.logger.error("aiohttp не установлен. Установите: pip install aiohttp")
            return []
        
        try:
            # Создаем таймаут из конфига
            timeout_obj = aiohttp.ClientTimeout(total=self.config.api.timeout)
            
            # Используем конструкцию async with для создания сессии
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                # Выполняем асинхронный GET запрос
                async with session.get(url) as response:
                    # Проверяем статус ответа
                    if response.status == 200:
                        # Читаем JSON ответ (тоже асинхронно)
                        data = await response.json()
                        return data
                    else:
                        self.logger.error(f"API вернуло статус {response.status} для {url}")
                        return []
        
        except asyncio.TimeoutError:
            self.logger.error(f"Таймаут при запросе к {url}")
            return []
        except aiohttp.ClientError as e:
            self.logger.error(f"Ошибка клиента при запросе к {url}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при запросе к {url}: {e}")
            return []


# Функция, которая экспортируется на уровне модуля для тестов
async def fetch_holidays_from_api(year: int, country_code: str) -> List[Dict[str, Any]]:
    """
    Асинхронная функция для получения праздников из API Nager.Date.
    Используется для удобного импорта в тестах.
    """
    config = get_default_config()
    handler = HolidayHandler(config=config)
    return await handler.fetch_holidays_from_api(year, country_code)