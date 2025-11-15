import logging
import json
import os
from datetime import datetime
from venv import logger

import pandas as pd
import requests as r
from typing import List, Dict
from pandas.tseries.offsets import BDay
from dateutil.relativedelta import relativedelta

def read_excel(file_name: str | None = None):
    """
    Считывает транзакции из Excel‑файла и возвращает pandas.DataFrame.

    Если file_name не указан – ищет файл  в папке
    ``data`` текущего проекта.

    Параметры
    ----------
    file_name : str, optional
        Имя файла (с расширением .xls или .xlsx). Путь считается
        относительно ``<project_root>/data/``.

    Возвращает
    -------
    pd.DataFrame | None
        DataFrame с данными или ``None`` при ошибке (файл не найден,
        неверный формат и т.п.). Ошибки логируются.
    """
    logger.info("Функция read_xlsx запущена.")
    file_dir = os.getcwd()
    if not file_name:
        file_path = os.path.join(file_dir, "data", "transactions.xlsx")
    else:
        file_path = os.path.join(file_dir, 'data', file_name)

    # Проверка существования файла
    if not os.path.isfile(file_path):
        logger.error(f"Ошибка! Файл {file_path} не найден.")
        return None
    # Проверка расширения файла
    if not file_path.endswith(".xlsx") and not file_path.endswith(".xls"):
        logger.error(f"Ошибка! Файл {file_path} не является Excel-файлом.")
        return None
    try:
        # Чтение Excel-файла
        data_frame = pd.read_excel(file_path)
        logger.info(f"Считывание Excel-файла успешно: {data_frame.shape[0]} записей загружено.")
        return data_frame
    except FileNotFoundError:
        logger.error(f"Ошибка! Файл {file_path} не найден.")
    except Exception as e:
        logger.critical(f"Неизвестная ошибка: {e}")
        return None
    finally:
        logger.info("Функция read_xlsx завершила работу.")

def greeting(date_: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток.

    Параметры
    ----------
    date_ : datetime
        Объект ``datetime`` с текущей датой/временем.

    Возвращает
    -------
    str
        Одно из: «Доброй ночи», «Доброе утро», «Добрый день», «Добрый вечер».
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

def top_transactions(data, start_date=None, end_date=None):
    """
        Возвращает JSON‑строку с топ‑5 расходных операций за указанный период.

        Параметры
        ----------
        data : pd.DataFrame или list[dict]
            Таблица транзакций.
        start_date, end_date : str, optional
            Даты в формате ``dd.mm.yyyy``. Если не указаны – берётся весь диапазон.

        Возвращает
        -------
        str
            JSON‑массив записей с полями ``date``, ``amount`` (положительная сумма),
            ``category``, ``description``.
        """

    if isinstance(data, list):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        return json.dumps([], ensure_ascii=False)

    # Точный парсинг даты — без warning
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
    data = data.dropna(subset=['Дата операции'])

    # Периоды
    if start_date:
        start_date = pd.to_datetime(start_date, format='%d.%m.%Y', errors='coerce') or pd.to_datetime(start_date)
    else:
        start_date = data['Дата операции'].min()

    if end_date:
        end_date = pd.to_datetime(end_date, format='%d.%m.%Y', errors='coerce') or pd.to_datetime(end_date)
    else:
        end_date = data['Дата операции'].max()

    # Фильтр: период + только расходы
    data = data[
        (data['Дата операции'] >= start_date) &
        (data['Дата операции'] <= end_date) &
        (data['Сумма операции'] < 0)
    ]

    if data.empty:
        return json.dumps([], ensure_ascii=False)

    data = data.copy()
    data['Сумма'] = data['Сумма операции'].abs()  # ← положительная сумма трат
    data = data.sort_values('Сумма', ascending=False).head(5)

    # ← ВОТ ГЛАВНОЕ ИЗМЕНЕНИЕ
    result = data[['Дата операции', 'Сумма', 'Категория', 'Описание']].rename(columns={
        'Дата операции': 'date',
        'Сумма': 'amount',           # теперь amount = 1500, а не -1500
        'Категория': 'category',
        'Описание': 'description'
    })

    result['date'] = result['date'].dt.strftime('%d.%m.%Y %H:%M')

    return result.to_json(orient='records', force_ascii=False, indent=4)


def cards(data, start_date=None, end_date=None):
    """
        Возвращает JSON‑строку с информацией по картам:
        последние 4 цифры, общие траты, кэшбэк (1 % от трат).

        Параметры
        ----------
        data : pd.DataFrame или list[dict]
            Таблица транзакций.
        start_date, end_date : str, optional
            Период в формате ``dd.mm.yyyy``.

        Возвращает
        -------
        str
            JSON‑массив объектов ``{last_digits, total_spent, cashback}``.
        """
    if isinstance(data, list):
        data = pd.DataFrame(data)
    elif not isinstance(data, pd.DataFrame):
        raise ValueError("Входные данные должны быть списком словарей или DataFrame.")

    # Фильтр по датам
    data['Дата операции'] = pd.to_datetime(data['Дата операции'], format='%d.%m.%Y %H:%M:%S', errors='coerce')
    data = data.dropna(subset=['Дата операции'])

    if start_date:
        start_date = pd.to_datetime(start_date, format='%d.%m.%Y', errors='coerce') or pd.to_datetime(start_date)
    else:
        start_date = data['Дата операции'].min()

    if end_date:
        end_date = pd.to_datetime(end_date, format='%d.%m.%Y', errors='coerce') or pd.to_datetime(end_date)
    else:
        end_date = data['Дата операции'].max()

    # Фильтр расходов + статус OK + период
    spends_only = data[
        (data['Дата операции'] >= start_date) &
        (data['Дата операции'] <= end_date) &
        (data['Сумма операции'] < 0) &
        (data['Статус'] == 'OK')
        ]

    cards_only = spends_only[spends_only['Номер карты'].notna()]

    # 🔥 ФИКС: суммируем ТОЛЬКО 'Сумма операции'
    card_sums = cards_only.groupby('Номер карты')['Сумма операции'].sum()

    # Остальное — как было
    card_sums = pd.DataFrame({'Сумма операции': card_sums})
    card_sums["Сумма операции"] = card_sums["Сумма операции"].apply(lambda x: -x)  # положительная
    card_sums["Номер карты"] = card_sums.index
    card_sums["Номер карты"] = card_sums["Номер карты"].apply(lambda x: str(x)[-4:])
    card_sums["Кэшбэк"] = card_sums["Сумма операции"] // 100


    response = card_sums[["Номер карты", 'Сумма операции', "Кэшбэк"]].rename(columns={
        "Номер карты": "last_digits",
        'Сумма операции': 'total_spent',
        "Кэшбэк": "cashback"
    }).to_json(force_ascii=False, indent=4, orient='records')

    return response

apilayer_key = 'uDBVLrs4Hzq1bOS6qsuq95UfBXauM95k'
headers = {'apikey':apilayer_key}
def currency_rates(currencies='USD,EUR'):
    """
        Получает курсы валют к RUB через API apilayer.com.

        Параметры
        ----------
        currencies : str | list[str]
            Запятая‑разделённый список или список кодов валют.

        Возвращает
        -------
        list[dict]
            Список ``{'currency': 'USD', 'rate': 92.34}`` (RUB → валюта).
        """
    # Если currencies - список, преобразуем в строку для params
    if isinstance(currencies, list):
        symbols = ','.join(currencies)
    else:
        symbols = currencies  # Уже строка

    params = {
        'base': 'RUB',
        'symbols': symbols
    }
    url = f"https://api.apilayer.com/exchangerates_data/latest"
    resp = r.get(url, headers=headers, params=params)
    if resp.status_code == 200:
        data = resp.json()
        # print(data)
    else:
        print("Error:", resp.status_code, resp.text)
    rates = []
    # Если currencies - список, итерация по списку; иначе - по split строки
    if isinstance(currencies, list):
        for cur in currencies:
            rates += [{"currency": cur, "rate": round(1 / data['rates'][cur], 2)}]
    else:
        for cur in currencies.split(','):
            rates += [{"currency": cur, "rate": round(1 / data['rates'][cur], 2)}]
    return rates

def stock_prices(stock_list: List[str] = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]) -> List[Dict[str, float]]:
    """
    Имитирует получение цен акций через Polygon.io (закрытие за предыдущий
    торговый день).

    Параметры
    ----------
    stock_list : list[str]
        Список тикеров.

    Возвращает
    -------
    list[dict]
        ``{'stock': 'AAPL', 'price': 175.43}``.
    """

    result = []
    apiKey = 'RMpdeqy6Ks0mDi_qRjsaLjnhtUikm1Da'
    today = datetime.today()
    # print(today.weekday())
    if today.weekday() == 0:
        day = today + relativedelta(days=-3)
    elif today.weekday() == 6:
        day = today + relativedelta(days=-2)
    else:
        day = today + relativedelta(days=-1)
    day = day - BDay(1)
    date = day.strftime("%Y-%m-%d")
    # print(date)
    # tickerlink = f'https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={apiKey}'
    for stock in stock_list:
        pricelink = f'https://api.polygon.io/v1/open-close/{stock}/{date}?apiKey={apiKey}'
        price = r.get(pricelink).json()['close']
        if price > 0:
            result.append({"stock": stock, "price": round(price, 2)})
    return result