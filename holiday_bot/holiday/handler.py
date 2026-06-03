import requests

# формат
# code = 'RU', 'US'
# year = 2025


def fetch_holidays_from_api(year: int, country_code: str):
    url = f"https://date.nager.at/api/v3/publicholidays/{year}/{country_code}"

    try:
        response = requests.get(url, timeout=10)
        holidays = response.json()
        return holidays
    except Exception as e:
        print(e)
