from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import BDay
from typing import List, Dict
from src.utils import stock_prices  # Импорт твоей функции
import pytest
from src.utils import currency_rates
import requests_mock
import json
import pandas as pd
from datetime import datetime
# Импорт вашей функции (замените на актуальный)
from src.utils import top_transactions  # Замените 'your_module' на имя файла с функцией
from src.utils import greeting, read_excel, top_transactions, cards, currency_rates, \
    stock_prices  # ← подправь путь, если нужно
import pytest
import pandas as pd
from datetime import datetime
import os
import json



def test_night():
    assert greeting(datetime(2025, 1, 1, 0, 0)) == "Доброй ночи"
    assert greeting(datetime(2025, 1, 1, 3, 30)) == "Доброй ночи"
    assert greeting(datetime(2025, 1, 1, 5, 59)) == "Доброй ночи"

def test_morning():
    assert greeting(datetime(2025, 1, 1, 6, 0)) == "Доброе утро"
    assert greeting(datetime(2025, 1, 1, 9, 15)) == "Доброе утро"
    assert greeting(datetime(2025, 1, 1, 11, 59)) == "Доброе утро"

def test_day():
    assert greeting(datetime(2025, 1, 1, 12, 0)) == "Добрый день"
    assert greeting(datetime(2025, 1, 1, 15, 45)) == "Добрый день"
    assert greeting(datetime(2025, 1, 1, 17, 59)) == "Добрый день"

def test_evening():
    assert greeting(datetime(2025, 1, 1, 18, 0)) == "Добрый вечер"
    assert greeting(datetime(2025, 1, 1, 21, 30)) == "Добрый вечер"
    assert greeting(datetime(2025, 1, 1, 23, 59)) == "Добрый вечер"

# tests/test_read_excel.py
import os
from pathlib import Path

import pandas as pd
import pytest

# ВАЖНО: поправь импорт ниже под свой проект
# Например: from bank_app.io_utils import read_excel



def _setup_cwd_to_tmp(tmp_path, monkeypatch):
    """Переносим cwd в tmp и создаем папку data/ как ожидает функция."""
    monkeypatch.setenv("PYTHONIOENCODING", "utf-8")
    monkeypatch.setattr(os, "getcwd", lambda: str(tmp_path))
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def test_read_excel_success_default_name(tmp_path, monkeypatch):
    """happy path: file_name is None -> data/transactions.xlsx, чтение успешно."""
    data_dir = _setup_cwd_to_tmp(tmp_path, monkeypatch)

    # делаем вид, что файл существует
    xlsx_path = data_dir / "transactions.xlsx"
    xlsx_path.touch()

    # мокаем pd.read_excel чтобы не читать настоящий excel
    df_mock = pd.DataFrame({"a": [1, 2, 3]})
    monkeypatch.setattr(pd, "read_excel", lambda path: df_mock)

    result = read_excel()
    assert isinstance(result, pd.DataFrame)
    assert result.equals(df_mock)


def test_read_excel_nonexistent_returns_none(tmp_path, monkeypatch):
    """если файла нет -> ранний None."""
    _setup_cwd_to_tmp(tmp_path, monkeypatch)
    # файла умышленно не создаем
    result = read_excel("missing.xlsx")
    assert result is None


def test_read_excel_wrong_extension_returns_none(tmp_path, monkeypatch):
    """если расширение не .xls/.xlsx -> ранний None."""
    data_dir = _setup_cwd_to_tmp(tmp_path, monkeypatch)
    bad = data_dir / "not_excel.txt"
    bad.touch()

    result = read_excel(bad.name)  # передаем имя 'not_excel.txt'
    assert result is None


def test_read_excel_raises_other_exception_returns_none(tmp_path, monkeypatch):
    """если pd.read_excel бросает любое исключение -> ловим except Exception -> None."""
    data_dir = _setup_cwd_to_tmp(tmp_path, monkeypatch)
    xlsx_path = data_dir / "ok.xlsx"
    xlsx_path.touch()

    def boom(_):
        raise ValueError("boom")

    monkeypatch.setattr(pd, "read_excel", boom)

    result = read_excel("ok.xlsx")
    assert result is None


def test_read_excel_file_not_found_race_returns_none(tmp_path, monkeypatch):
    """
    редкий кейс: гонка — isfile -> True, а затем при чтении FileNotFoundError.
    эмулируем isfile=True и заставляем pd.read_excel бросить FileNotFoundError.
    """
    _setup_cwd_to_tmp(tmp_path, monkeypatch)

    # isfile всегда True, даже если физического файла нет
    monkeypatch.setattr(os.path, "isfile", lambda p: True)

    def missing(_):
        raise FileNotFoundError("disappeared")

    monkeypatch.setattr(pd, "read_excel", missing)

    result = read_excel("ghost.xlsx")
    assert result is None

# Fixture для базовых данных (в формате, ожидаемом функцией)
@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'Дата операции': [
            '01.08.2025 10:00:00', '02.08.2025 11:00:00', '03.08.2025 12:00:00',
            '04.08.2025 13:00:00', '05.08.2025 14:00:00', '06.08.2025 15:00:00',
            '07.08.2025 16:00:00'  # >5 для теста топ-5
        ],
        'Сумма операции': [-1000, -2000, -1500, -3000, -2500, 1000, -500],  # Расходы (<0) и доход (>0)
        'Категория': ['Cat1', 'Cat2', 'Cat3', 'Cat4', 'Cat5', 'Cat6', 'Cat7'],
        'Описание': ['Desc1', 'Desc2', 'Desc3', 'Desc4', 'Desc5', 'Desc6', 'Desc7']
    })

# Тест 1: Invalid input type -> empty JSON (покрывает else в проверке типа)
def test_invalid_input_type():
    result = top_transactions("not_a_df_or_list")
    assert result == json.dumps([], ensure_ascii=False)

# Тест 2: Input as list of dicts -> convert to DF (покрывает if isinstance(list))
def test_input_as_list(sample_data):
    data_list = sample_data.to_dict(orient='records')
    result = top_transactions(data_list)
    parsed = json.loads(result)
    assert len(parsed) == 5  # Топ-5 расходов
    assert parsed[0]['amount'] == 3000  # Абсолютная сумма, sorted desc

# Тест 3: Default dates (min/max from data) (покрывает default start/end)
def test_default_dates(sample_data):
    result = top_transactions(sample_data)
    parsed = json.loads(result)
    assert len(parsed) == 5
    assert parsed[0]['date'] == '04.08.2025 13:00'  # Топ по abs sum
    assert parsed[0]['amount'] == 3000
    assert parsed[0]['category'] == 'Cat4'
    assert parsed[0]['description'] == 'Desc4'

# Тест 4: Custom dates (фильтр по периоду) (покрывает custom parsing start/end)
def test_custom_dates(sample_data):
    result = top_transactions(sample_data, start_date='02.08.2025', end_date='05.08.2025')
    parsed = json.loads(result)
    assert len(parsed) == 4
    assert parsed[0]['amount'] == 3000
    assert parsed[3]['amount'] == 1500

# Тест 5: No expenses in data (all positive or zero) (покрывает data.empty after filter)
def test_no_expenses():
    data = pd.DataFrame({
        'Дата операции': ['01.08.2025 10:00:00'],
        'Сумма операции': [1000],  # Положительная
        'Категория': ['Cat'],
        'Описание': ['Desc']
    })
    result = top_transactions(data)
    assert result == json.dumps([], ensure_ascii=False)

# !Тест 6: Empty DataFrame (покрывает data.empty early)
def test_empty_dataframe():
    data =  pd.DataFrame({
        'Дата операции': [],
        'Сумма операции': [],  # Расходы (<0) и доход (>0)
        'Категория': [],
        'Описание': []
    })

    result = top_transactions(data)
    assert result == json.dumps([], ensure_ascii=False)


# Тест 7: Less than 5 expenses (покрывает head(5) с меньшим кол-вом)
def test_less_than_5_expenses(sample_data):
    # Фильтр только 3 расхода
    result = top_transactions(sample_data, start_date='01.08.2025', end_date='03.08.2025')
    parsed = json.loads(result)
    assert len(parsed) == 3 #почему 2
    assert parsed[0]['amount'] == 2000  # Sorted desc


# !Тест 8: NaT in dates (dropna) (покрывает errors='coerce' и dropna)
def test_nat_in_dates():
    data = pd.DataFrame({
        'Дата операции': ['invalid_date', '01.08.2025 10:00:00', '02.08.2025 11:00:00'],
        'Сумма операции': [-1000, -2000, -1500],
        'Категория': ['Cat1', 'Cat2', 'Cat3'],
        'Описание': ['Desc1', 'Desc2', 'Desc3']
    })
    result = top_transactions(data)
    parsed = json.loads(result)
    assert len(parsed) == 2

# Тест 10: All data filtered out by dates (покрывает filter -> empty)
def test_dates_out_of_range(sample_data):
    result = top_transactions(sample_data, start_date='10.08.2025', end_date='15.08.2025')
    assert result == json.dumps([], ensure_ascii=False)

# Тест 11: Positive amounts after abs (покрывает copy и abs)
def test_positive_amounts(sample_data):
    result = top_transactions(sample_data)
    parsed = json.loads(result)
    for item in parsed:
        assert item['amount'] > 0  # Все положительные

# Тест 12: Date formatting in output
def test_date_formatting(sample_data):
    result = top_transactions(sample_data)
    parsed = json.loads(result)
    assert parsed[0]['date'] == '04.08.2025 13:00'  # %d.%m.%Y %H:%M


# Фикстура: нормальные данные (DataFrame с транзакциями)
@pytest.fixture
def sample_df():
    data = {
        'Дата операции': ['01.08.2025 10:00:00', '02.08.2025 11:00:00', '03.08.2025 12:00:00', '04.08.2025 13:00:00'],
        'Сумма операции': [-1000, -2000, 500, -1500],  # Расходы и доход
        'Статус': ['OK', 'OK', 'OK', 'FAIL'],  # Разные статусы
        'Номер карты': ['1234567812345678', '1234567812345678', '8765432187654321', None]  # Две карты + NaN
    }
    return pd.DataFrame(data)


# Фикстура: данные как список словарей
@pytest.fixture
def sample_list():
    return [
        {'Дата операции': '01.08.2025 10:00:00', 'Сумма операции': -1000, 'Статус': 'OK',
         'Номер карты': '1234567812345678'},
        {'Дата операции': '02.08.2025 11:00:00', 'Сумма операции': -2000, 'Статус': 'OK',
         'Номер карты': '1234567812345678'},
        {'Дата операции': '03.08.2025 12:00:00', 'Сумма операции': 500, 'Статус': 'OK',
         'Номер карты': '8765432187654321'},
        {'Дата операции': '04.08.2025 13:00:00', 'Сумма операции': -1500, 'Статус': 'FAIL', 'Номер карты': None}
    ]


# Тест 1: Нормальный DataFrame без дат (весь период)
def test_cards_with_dataframe(sample_df):
    result = cards(sample_df)
    parsed = json.loads(result)

    # Ожидаемый: только расходы, OK, не NaN карты. Сумма по первой карте: 1000+2000=3000, кэшбэк=30
    expected = [
        {"last_digits": "5678", "total_spent": 3000.0, "cashback": 30.0}
    ]
    assert parsed == expected  # Сравниваем parsed JSON


# Тест 2: Данные как список (конвертация в DataFrame)
def test_cards_with_list(sample_list):
    result = cards(sample_list)
    parsed = json.loads(result)

    expected = [
        {"last_digits": "5678", "total_spent": 3000.0, "cashback": 30.0}
    ]
    assert parsed == expected


# Тест 3: Неправильный тип data (raise ValueError)
def test_cards_invalid_type():
    with pytest.raises(ValueError, match="Входные данные должны быть списком словарей или DataFrame."):
        cards("not a dataframe or list")  # Строка — неверный тип


# Тест 4: С указанными датами (фильтр периода)
def test_cards_with_dates(sample_df):
    start_date = '02.08.2025'  # Только вторая транзакция
    end_date = '03.08.2025'
    result = cards(sample_df, start_date, end_date)
    parsed = json.loads(result)

    # Только вторая: -2000 на первой карте
    expected = [
        {"last_digits": "5678", "total_spent": 2000.0, "cashback": 20.0}
    ]
    assert parsed == expected


# Тест 5: Пустой DataFrame (нет данных — пустой JSON)
def test_cards_empty_dataframe():
    empty_df = pd.DataFrame(columns=['Дата операции', 'Сумма операции', 'Статус', 'Номер карты'])
    result = cards(empty_df)
    parsed = json.loads(result)
    assert parsed == []  # Пустой список


# Тест 6: NaN в датах или суммах (dropna и фильтры)
def test_cards_with_nan(sample_df):
    # Добавим NaN в дату и сумму
    sample_df.loc[0, 'Дата операции'] = None  # NaN дата → drop
    sample_df.loc[1, 'Сумма операции'] = None  # NaN сумма → не расход
    result = cards(sample_df)
    parsed = json.loads(result)

    # Останется только ничего (поскольку первая drop, вторая NaN сумма, третья доход, четвёртая FAIL/NaN)
    assert parsed == []


# Тест 7: Несколько карт, проверка маскировки и кэшбэка
def test_cards_multiple_cards():
    data = {
        'Дата операции': ['01.08.2025 10:00:00', '02.08.2025 11:00:00'],
        'Сумма операции': [-500, -300],
        'Статус': ['OK', 'OK'],
        'Номер карты': ['1111222233334444', '5555666677778888']
    }
    df = pd.DataFrame(data)
    result = cards(df)
    parsed = json.loads(result)

    expected = [
        {"last_digits": "4444", "total_spent": 500.0, "cashback": 5.0},
        {"last_digits": "8888", "total_spent": 300.0, "cashback": 3.0}
    ]
    # Сортировка не гарантирована, так что сортируем для сравнения
    parsed_sorted = sorted(parsed, key=lambda x: x['last_digits'])
    expected_sorted = sorted(expected, key=lambda x: x['last_digits'])
    assert parsed_sorted == expected_sorted





def test_currency_rates_default_string_input():
    """Тест с дефолтным параметром: строка 'USD,EUR'"""
    result = currency_rates()  # без аргументов → 'USD,EUR'

    assert isinstance(result, list)
    assert len(result) == 2

    currencies = {item["currency"] for item in result}
    assert "USD" in currencies
    assert "EUR" in currencies

    # Курс должен быть положительным и реалистичным (на 2025 год)
    for item in result:
        assert isinstance(item["currency"], str)
        assert isinstance(item["rate"], float)
        assert item["rate"] > 50  # RUB → USD/EUR обычно >50 в 2025
        assert item["rate"] < 200  # не больше 200, если не кризис :)


def test_currency_rates_string_input():
    """Тест с явной строкой"""
    result = currency_rates("USD,GBP,JPY")

    assert len(result) == 3
    expected = {"USD", "GBP", "JPY"}
    actual = {item["currency"] for item in result}
    assert actual == expected


def test_currency_rates_list_input():
    """Тест с передачей списка → проверяем ветку if isinstance(list)"""
    result = currency_rates(["USD", "CNY", "KZT"])

    assert len(result) == 3
    expected = {"USD", "CNY", "KZT"}
    actual = {item["currency"] for item in result}
    assert actual == expected


def test_currency_rates_single_currency_string():
    """Тест с одной валютой в строке"""
    result = currency_rates("CHF")

    assert len(result) == 1
    assert result[0]["currency"] == "CHF"
    assert isinstance(result[0]["rate"], float)


def test_currency_rates_single_currency_list():
    """Тест с одной валютой в списке"""
    result = currency_rates(["AUD"])

    assert len(result) == 1
    assert result[0]["currency"] == "AUD"
    assert result[0]["rate"] > 40  # грубо, но работает


def test_stock_prices_default_list_success():
    """
    Все дефолтные тикеры, все цены положительные.
    Ожидаем: в результате будут все тикеры.
    """
    # Фейковый ответ requests.get
    fake_response = MagicMock()
    fake_response.json.return_value = {"close": 123.45}

    # Патчим r.get в том модуле, где объявлена функция stock_prices
    with patch("src.utils.r.get", return_value=fake_response):
        result = stock_prices()

    # Дефолтный список: ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    assert isinstance(result, list)
    assert len(result) == 5

    tickers = [item["stock"] for item in result]
    for ticker in ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]:
        assert ticker in tickers

    for item in result:
        assert item["price"] == 123.45

def test_stock_prices_filters_non_positive_prices():
    """
    Часть тикеров возвращает цену 0 или < 0.
    Ожидаем: в результат попадут только тикеры с ценой > 0.
    """
    stocks: List[str] = ["AAPL", "TSLA", "MSFT"]

    def fake_get(url: str) -> MagicMock:
        resp = MagicMock()
        if "AAPL" in url:
            resp.json.return_value = {"close": 150.0}
        elif "TSLA" in url:
            resp.json.return_value = {"close": 0.0}
        else:  # MSFT
            resp.json.return_value = {"close": -10.0}
        return resp

    with patch("src.utils.r.get", side_effect=fake_get):
        result = stock_prices(stocks)

    tickers_result = [item["stock"] for item in result]

    assert "AAPL" in tickers_result
    assert "TSLA" not in tickers_result
    assert "MSFT" not in tickers_result
    assert len(tickers_result) == 1
    # проверяем округление и значение
    assert result[0]["price"] == 150.0


def test_stock_prices_uses_custom_stock_list():
    """
    Передаём свой список тикеров и проверяем,
    что в результат попали только они и с правильными ценами.
    """
    stocks: List[str] = ["NFLX", "NVDA"]

    price_map: Dict[str, float] = {
        "NFLX": 321.987,
        "NVDA": 999.499,
    }

    def fake_get(url: str) -> MagicMock:
        resp = MagicMock()
        if "NFLX" in url:
            resp.json.return_value = {"close": price_map["NFLX"]}
        else:
            resp.json.return_value = {"close": price_map["NVDA"]}
        return resp

    with patch("src.utils.r.get", side_effect=fake_get):
        result = stock_prices(stocks)

    assert len(result) == 2

    result_map = {item["stock"]: item["price"] for item in result}
    assert result_map["NFLX"] == round(price_map["NFLX"], 2)
    assert result_map["NVDA"] == round(price_map["NVDA"], 2)