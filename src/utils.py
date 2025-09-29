import logging
from datetime import datetime
from typing import Dict

import pandas as pd

logging.basicConfig(level=logging.INFO)


def greeting(date_: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток на основе объекта datetime.

    Args:
        date_ (datetime): Объект datetime с датой и временем.

    Returns:
        str: Приветствие ('Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи').
    """
    logging.info("Обработка времени: %s", date_)

    hour = date_.hour
    if 0 <= hour < 6:
        return "Доброй ночи"
    if 6 <= hour < 12:
        return "Доброе утро"
    if 12 <= hour < 18:
        return "Добрый день"
    return "Добрый вечер"

def read_transactions(file_path: str) -> pd.DataFrame:
    """Читает Excel-файл с транзакциями (operations.xls) и
    возвращает DataFrame (pandas). Обрабатывает ошибки чтения,
    логирует их. """
    pass

def get_currency_rate(currency: str) -> float:
    """Получает курс валюты (USD/EUR) через API (requests).
    Читает список валют из user_settings.json.
    Логирует запросы и ошибки."""
    pass

def get_stock_price(stock: str) -> float:
    """Получает цену акции (AAPL, AMZN и т.д.) через API (requests).
    Читает список акций из user_settings.json. Логирует запросы. """
    pass

def filter_by_date(df: pd.DataFrame, start_date: datetime, end_date: datetime) -> pd.DataFrame:
    """Фильтрует транзакции в DataFrame по диапазону дат
    (использует datetime). Учитывает колонку "Дата операции". """
    pass

def log_error(message: str) -> None:
    """Логирует ошибки в файл или консоль (logging).
    Форматирует сообщения с временной меткой."""
    pass

def load_json_settings(file_path: str) -> Dict:
    """Загружает настройки (валюты, акции) из user_settings.json.
    Возвращает словарь. Логирует ошибки чтения."""
    pass
