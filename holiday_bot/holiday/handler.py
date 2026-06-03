import aiohttp
import asyncio
import logging
import requests

from holiday_bot.holiday.config import APIConfig, LoggingConfig

# формат
# code = 'RU', 'US'
# year = 2025

logging.basicConfig(
    format=LoggingConfig.format,
    level=LoggingConfig.level
)
logger = logging.getLogger(__name__)


async def fetch_holidays_from_api(year: int, country_code: str):
    api = APIConfig()
    url = f"{api.base_url}/{year}/{country_code}"
