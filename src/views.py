import json
from typing import Dict, Any

from src.services import top_cashback_categories, top_cashback_categories_count, investment_bank_sum, \
    investment_bank_smart_step, investment_bank_count, simple_search

# Настройка логирования
import logging
import pandas as pd
from datetime import datetime, time

from src.utils import greeting

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename="app.log", format="%(asctime)s - %(levelname)s - %(message)s")


def home_page(current_date_str=None):
    current_date = datetime.now()
    greeting_message = greeting(current_date)
    # Выводим результат
    print(greeting_message)
    return greeting_message

home_page()


def events_page(df: pd.DataFrame, period: str = 'M') -> Dict:
    """ Генерирует JSON для страницы "Главная". Принимает дату-время (YYYY-MM-DD HH:MM:SS). Возвращает приветствие, данные по картам (последние 4 цифры, сумма трат, кешбэк),
  топ-5 транзакций по сумме платежа, курсы валют и цены акций. Использует pandas, requests,
  json, datetime, logging.
  """
pass




