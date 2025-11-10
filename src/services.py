import json
import math
import re
from datetime import timedelta, datetime
from typing import List, Dict, Any
from venv import logger

import pandas as pd

from src.utils import read_excel

def top_cashback_categories(data, year, month):
    logger.info("Запущена функция top_cashback_categories за  месяц=%s, год=%s", month, year)
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], dayfirst=True, errors='coerce')
    filtered_data = data[(data['Дата операции'].dt.month == month) & (data['Дата операции'].dt.year == year)]
    #data = data[data['Дата операции'].notna()]
    cashback_cats  = {}
    cashbacks = filtered_data[(filtered_data['Статус'] == 'OK') & (filtered_data['Кэшбэк'].notna())]
    total_cashbacks = cashbacks.groupby('Категория')['Кэшбэк'].sum().reset_index()
    for index, row in total_cashbacks.iterrows():
        cashback_cats[row['Категория']] = row['Кэшбэк']
    #total_cashbacks = (cashbacks.groupby('Категория', as_index=False)['Кэшбэк'].sum().round(2))
    #cashback_cats = dict(sorted(total_cashbacks.itertuples(index=False, name=None), key=lambda x: x[1], reverse=True))
    resalt =  json.dumps(cashback_cats, indent=4, ensure_ascii=False) #total_cashbacks.to_json(force_ascii=False, indent=4, orient='records') #return json.dumps(dict(sorted(cashback_cats.items(), key=lambda x: x[1], reverse=True)),indent=4, ensure_ascii=False)
    logger.info("Функция завершена. Возвращаем JSON с %s категориями", len(cashback_cats))
    return resalt

def investment_bank(month: str, data, limit: int) -> float:
    logger.info("Запуск функции investment_bank: месяц и год=%s, шаг округления=%s", month, limit)
    if isinstance(data, list):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        logger.error("Ошибка: входные данные не список и не DataFrame.")
        raise ValueError("Входные данные должны быть списком словарей или DataFrame.")
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], dayfirst=True, errors='coerce')
    m, y = [int(i) for i in month.split('.')]
    filtered_data = data[(data['Дата операции'].dt.month == m) & (data['Дата операции'].dt.year == y)]
    legit_transactions = filtered_data[
        (filtered_data['Округление на инвесткопилку'] != 0) & (filtered_data['Сумма операции'] < 0)].copy()
    legit_transactions['Накоплено'] = legit_transactions['Сумма операции'].apply(lambda x: limit - (-x) % limit)
    resalt = legit_transactions['Накоплено'].sum()
    logger.info("Расчёт завершён. Всего накоплено на инвесткопилку: %.2f руб.", resalt)
    return resalt


def search_phones(data, start_date=None, end_date=None):
    """Ищет транзакции с мобильными номерами в описании (формат: +7 xxx xx-xx-xx). Возвращает JSON-список транзакций. Использует json, re, logging.
  """
    logger.info("Запуск функции search_phones: start_date=%s, end_date=%s", start_date, end_date)

    # Конвертация в DataFrame
    if isinstance(data, list):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        logger.error("Ошибка: входные данные не список и не DataFrame.")
        raise ValueError("Входные данные должны быть списком словарей или DataFrame.")

    # Фильтр по датам
    # Даты — строки → datetime
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], dayfirst=True, errors='coerce')
    data = data.dropna(subset=['Дата операции'])

    # Период — строки → datetime
    start = pd.to_datetime(start_date, dayfirst=True) if start_date else data['Дата операции'].min()
    end = pd.to_datetime(end_date, dayfirst=True) if end_date else data['Дата операции'].max()

    result = data[
        (data['Статус'] == 'OK') &
        (data['Категория'] == 'Переводы') &
        (data['Дата операции'].between(start, end)) &
        data['Описание'].str.contains(r'\+7\s?\d{3}\s?\d{2}-\d{2}-\d{2}', regex=True, na=False, flags=re.IGNORECASE)
        ].copy()

    # Дата
    result['Дата операции'] = result['Дата операции'].dt.strftime('%d.%m.%Y')

    logger.info("Поиск завершён")

    return result.to_json(force_ascii=False, indent=4, orient='records')

def text_search(data, search_word=None, start_date=None, end_date=None):
    """Ищет транзакции, где строка query есть в описании или категории. Возвращает JSON-список транзакций. Использует json, logging.
  """
    logger.info("Запуск функции text_search: search_word='%s', start_date=%s, end_date=%s",
                search_word, start_date, end_date)
    df = pd.DataFrame(data)
    # Даты — строки → datetime
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], dayfirst=True, errors='coerce')
    data = data.dropna(subset=['Дата операции'])
    # Период — строки → datetime
    start = pd.to_datetime(start_date, dayfirst=True) if start_date else data['Дата операции'].min()
    end = pd.to_datetime(end_date, dayfirst=True) if end_date else data['Дата операции'].max()
    filtered = data[
        data['Категория'].notna() &
        data['Описание'].notna() &
        (data['Дата операции'] >= start) &
        (data['Дата операции'] <= end)
        ]
    filtered['Дата операции'] = filtered['Дата операции'].dt.strftime('%d.%m.%Y')
    if search_word:
        word = search_word.strip().lower()
        with_word = filtered[(filtered['Описание'].str.lower().str.contains(word, na=False)) | (filtered['Категория'].str.lower().str.contains(word, na=False))  ]
    else:
        with_word = pd.DataFrame()
    return with_word.to_json(force_ascii=False, orient='records', indent=4)


def transfer_search(data, start_date=None, end_date=None):
    """Ищет переводы. Всё — строки. Никаких миллисекунд."""
    logger.info("Запуск функции transfer_search: start_date=%s, end_date=%s", start_date, end_date)
    df = pd.DataFrame(data)

    # Даты — строки → datetime
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Дата операции'])
    # Период — строки → datetime
    start = pd.to_datetime(start_date, dayfirst=True) if start_date else df['Дата операции'].min()
    end = pd.to_datetime(end_date, dayfirst=True) if end_date else df['Дата операции'].max()

    # Фильтр
    result = df[
        (df['Статус'] == 'OK') &
        (df['Категория'] == 'Переводы') &
        (df['Дата операции'].between(start, end)) &
        df['Описание'].str.contains(r'[А-ЯЁ][а-яё]+(?:\s[А-ЯЁ]\.){1,2}', regex=True, flags=re.IGNORECASE)
        ].copy()

    # Красивая дата
    result['Дата операции'] = result['Дата операции'].dt.strftime('%d.%m.%Y')
    logger.info("Поиск переводов завершён. Найдено %d операций физлицам.", len(result))
    return result.to_json(force_ascii=False, indent=4, orient='records')

