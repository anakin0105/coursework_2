import json
from typing import Dict, Any

from openpyxl.styles.builtins import currency

from src.services import top_cashback_categories
# Настройка логирования
import logging
import pandas as pd
from datetime import datetime, time

from src.utils import greeting, top_transactions, cards, currency_rates, stock_prices

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename="../app.log", format="%(asctime)s - %(levelname)s - %(message)s")




def home_page(data,start_date=None, end_date=None, currencies = ['USD','EUR'],):
    response = {}
    current_date = datetime.now()
    # фильтр за месяц
    response['greeting']= greeting(current_date)
    response['cards'] = cards(data, start_date, end_date) # считает по формуле 100 рубль 1 рубль
    response['top_transactions'] = top_transactions(data, start_date, end_date)
    response['currency_rates'] = currency_rates(','.join(currencies))
    response['stock_prices'] = stock_prices()
    return json.dumps(response, indent=4, ensure_ascii=False).replace('\\"','"').replace("\\n", "\n")



def events_page(df: pd.DataFrame, period: str = 'M') -> Dict:
    """ Генерирует JSON для страницы "Главная". Принимает дату-время (YYYY-MM-DD HH:MM:SS). Возвращает приветствие, данные по картам (последние 4 цифры, сумма трат, кешбэк),
  топ-5 транзакций по сумме платежа, курсы валют и цены акций. Использует pandas, requests,
  json, datetime, logging.
  """
pass




