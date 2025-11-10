import json
import re
import os
import logging
import pandas as pd
import warnings
import datetime
from datetime import datetime,timedelta, date
from dateutil.relativedelta import relativedelta
from functools import wraps
from typing import Optional, Callable, List, Dict, Any
from src.utils import read_excel, top_transactions, cards, greeting, currency_rates, stock_prices
from src.services import top_cashback_categories, search_phones,investment_bank, transfer_search, text_search
from src.reports import spending_by_weekday, spending_by_catеgory,spending_by_workday
from src.views import home_page
#warnings.simplefilter(action='ignore')

# ЛОГИРОВАНИЕ
logger = logging.getLogger('Main_logger')
logger.setLevel(logging.DEBUG)
# log_dir = os.path.join(os.path.dirname(os.path.abspath(file)), "..", "logs")
# log_file = os.path.join(log_dir, "utils.log")
file_handler = logging.FileHandler('app.log', mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s","%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

#ЧТЕНИЕ ФАЙЛА
data = read_excel("1.xls")

print(home_page(data,'01.08.2025', '08.08.2025'))

#services
#print(top_cashback_categories(data, 2025, 8))
#print(investment_bank('08.2025', data, 50))
#print(search_phones(data, '01.08.2025','08.08.2025'))
#print(transfer_search(data,'18.08.2025','30.08.2025'))
#print(text_search(data, "МТС"))

#reports




# def load_json_settings(file_path: str) -> Dict:
#     """Загружает настройки (валюты, акции) из user_settings.json.
#     Возвращает словарь. Логирует ошибки чтения.
#     """
#     with open(file_path, 'r', encoding='utf-8') as f:
#         settings = json.load(f)
#         return settings
