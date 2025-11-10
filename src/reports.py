from functools import wraps
from venv import logger

import pandas as pd
from datetime import datetime
from typing import Optional
import json

from dateutil.relativedelta import relativedelta


def report_logger(file_name=None):
    # Если декоратор вызвали без параметра
    if callable(file_name):
        func = file_name
        default_filename = f"report_{datetime.today().strftime("%Y-%m-%d_%H-%M-%S")}.txt"

        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open(default_filename, "a", encoding="utf-8") as f:
                f.write(f"{result}\n{'-'*40}\n")
            # === JSON (поддержка DataFrame) ===
            json_filename = default_filename.rsplit('.', 1)[0] + '.json'
            with open(json_filename, "a", encoding="utf-8") as f:
                if isinstance(result, pd.DataFrame):
                    # Превращаем DataFrame в JSON-строку
                    json_str = result.to_json(force_ascii=False, orient='records', date_format='iso', indent=4)
                    f.write(json_str + '\n')  # записываем как строку + новая строка
                else:
                    # Если не DataFrame — обычный json.dump
                    json.dump(result, f, ensure_ascii=False, indent=4)
                    f.write('\n')
            return result

        return wrapper

    # Если декоратора вызвали с параметром (имя файла)
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            filename = file_name or f"report_{datetime.today().strftime("%Y-%m-%d_%H-%M-%S")}.txt"
            with open(filename, "a", encoding="utf-8") as f:
                f.write(f"{result}\n{'-'*40}\n")
                # === JSON (поддержка DataFrame) ===
            json_filename = filename.rsplit('.', 1)[0] + '.json'
            with open(json_filename, "a", encoding="utf-8") as f:
                if isinstance(result, pd.DataFrame):
                    # Превращаем DataFrame в JSON-строку
                    json_str = result.to_json(force_ascii=False, orient='records', date_format='iso', indent=4)
                    f.write(json_str + '\n')  # записываем как строку + новая строка
                else:
                    # Если не DataFrame — обычный json.dump
                    json.dump(result, f, ensure_ascii=False, indent=4)
                    f.write('\n')
            return result
        return wrapper

    return decorator

@report_logger
def spending_by_catеgory(data: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    logger.info("Функция spending_by_catеgory запущена.")
    operations_by_catigories = data[(data['Категория'] == category) & (data['Сумма операции'] < 0)].copy()
    operations_by_catigories['Дата операции'] = pd.to_datetime(operations_by_catigories['Дата операции'], dayfirst=True, errors='coerce')
    if date:
        d,m,y = [int(x) for x in date.split('.')]
        start_date = date(y,m,d)
        end_date = start_date + relativedelta(months=3)
    else:
        end_date = datetime.today()
        start_date = end_date + relativedelta(months=-3)
    operations_by_catigories = operations_by_catigories[(operations_by_catigories['Дата операции'] >= start_date) & (operations_by_catigories['Дата операции'] < end_date)]
    logger.info("Функция spending_by_category завершена.")
    return operations_by_catigories


@report_logger
def spending_by_weekday(data: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    logger.info("Функция spending_by_weekday запущена.")
    operations_by_catigories = data[(data['Сумма операции'] < 0)].copy()
    # print(operations_by_catigories)
    operations_by_catigories['Дата операции'] = pd.to_datetime(operations_by_catigories['Дата операции'], dayfirst=True,
                                                               errors='coerce')
    if date:
        d, m, y = [int(x) for x in date.split('.')]
        start_date = datetime(y, m, d)
        end_date = start_date + relativedelta(months=3)
    else:
        end_date = datetime.today()
        start_date = end_date + relativedelta(months=-3)
    operations_by_catigories = operations_by_catigories[(operations_by_catigories['Дата операции'] >= start_date) & (
                operations_by_catigories['Дата операции'] < end_date)]
    # print( operations_by_catigories)
    operations_by_catigories['Дни недели'] = operations_by_catigories[
        'Дата операции'].dt.weekday  # .map({0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'})
    # print(operations_by_catigories.head(50))
    grouped = operations_by_catigories.groupby('Дни недели')['Сумма операции'].mean().round(2).to_frame('Средние траты')
    grouped['Дни недели'] = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    logger.info("Функция spending_by_weekday завершила работу.")
    grouped_2 = grouped[['Дни недели', 'Средние траты']].reset_index(drop=True)
    # grouped = grouped.assign(Дни=['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']).set_index(['Дни'], append=True)

    # Группировка: сумма абсолютных трат
    # grouped = (operations_by_catigories.groupby('weekday')['Сумма операции'].apply(lambda x: round(-x.sum(), 2)).reset_index(name='Траты'))
    # #grouped = operations_by_catigories.groupby('weekday').agg({'Сумма операции': lambda x: round(-x.sum(), 2)})# -x.sum() делает положительной
    # grouped['weekday'] = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    # #grouped = grouped.assign(Дни=['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']).set_index(['Дни'], append=True)
    return grouped_2


@report_logger
def spending_by_workday(data: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    logger.info("Функция  spending_by_workday запущена.")
    operations_by_catigories = data[(data['Сумма операции'] < 0) & (data['Категория'] != 'Переводы')].copy()
    operations_by_catigories['Дата операции'] = pd.to_datetime(operations_by_catigories['Дата операции'], dayfirst=True,
                                                               errors='coerce')
    if date:
        d, m, y = [int(x) for x in date.split('.')]
        start_date = date(y, m, d)
        end_date = start_date + relativedelta(months=3)
    else:
        end_date = datetime.today()
        start_date = end_date + relativedelta(months=-3)
        # День недели: 0=понедельник, 6=воскресенье
    operations_by_catigories = operations_by_catigories[(operations_by_catigories['Дата операции'] >= start_date) & (
                operations_by_catigories['Дата операции'] < end_date)]
    operations_by_catigories['Сумма'] = operations_by_catigories['Сумма операции']
    operations_by_catigories['День недели'] = operations_by_catigories['Дата операции'].dt.weekday.map(
        lambda x: 'Рабочий' if x < 5 else 'Выходной')
    # print( operations_by_catigories.head(30))
    avg_by_day = operations_by_catigories.groupby('День недели')['Сумма'].mean().round(2).to_frame(
        'Средние траты').reset_index()
    # print(avg_by_day)
    # operations_by_catigories['День недели'] = operations_by_catigories['Дата операции'].dt.weekday.map(lambda x: 'Рабочий' if x < 5 else 'Выходной')
    # # Группировка: трат
    # result = operations_by_catigories.groupby('День недели')['Сумма операции'].apply(lambda x: round(-x.mean(), 2))
    logger.info("Функция  spending_by_workday завершила работу.")
    return avg_by_day

    # operations_by_catigories ['weekday'] = operations_by_catigories ['Дата операции'].dt.weekday.apply(lambda x: 'Рабочий' if x < 6 else 'Выходной')
    # result = operations_by_catigories.groupby('weekday')['Сумма операции'].apply(lambda x: round(-x.mean(), 2)).reindex(['Рабочий', 'Выходной']).to_frame('Средние траты')
    # result = (operations_by_catigories.groupby('weekday')['Сумма операции'].apply(lambda x: round(-x.mean(), 2))avg_by_day

    # return result
