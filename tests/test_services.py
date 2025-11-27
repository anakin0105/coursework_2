import pytest
import pandas as pd
import json
from datetime import datetime

from src.services import (
    top_cashback_categories,
    investment_bank,
    search_phones,
    text_search,
    transfer_search)


@pytest.fixture
def sample_df():
    data = {
        'Дата операции': [
            '01.08.2025 10:30:00', '15.08.2025 14:20:00', '20.08.2025 09:15:00',
            '10.08.2025 12:00:00', '10.08.2025 18:45:00'
        ],
        'Статус': ['OK', 'OK', 'OK', 'OK', 'OK'],
        'Сумма операции': [-1500.0, -237.0, -890.0, -500.0, -320.0],
        'Кэшбэк': [75.0, 0, 44.5, 25.0, 0],
        'Категория': ['Супермаркеты', 'Транспорт', 'Рестораны', 'Супермаркеты', 'Переводы'],
        'Описание': [
            'Пятерочка', 'Яндекс Такси', 'Burger King', 'Магнит', 'Перевод Иванову И.И.'
        ],
        'Округление на инвесткопилку': [50, 13, 10, 0, 30],
        'Номер карты': ['123456****7890', '123456****7890', None, '123456****7890', '123456****7890']
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
    return df





def test_top_cashback_categories(sample_df):
    result = top_cashback_categories(sample_df, 2025, 8)
    data = json.loads(result)

    assert isinstance(data, dict)
    assert 'Супермаркеты' in data
    assert data['Супермаркеты'] == 100.0
    assert data['Рестораны'] == 44.5
    # порядок не важен, но сумма точная


def test_investment_bank(sample_df):
    result = investment_bank('08.2025', sample_df, 50)
    # -1500 → 0 (кратно), -237 → 13 → в копилку 37, -320 → 30 → в копилку 20
    # ожидаем: 37 + 20 = 57 (если только те, где 'Округление' != 0)
    assert result == 103.0


def test_search_phones(sample_df):
    # добавим одну строку с телефоном
    sample_df.loc[5] = [pd.Timestamp('2025-08-10'), 'OK', -1000, 0, 'Переводы',
                        'Пополнение +7 999 88-77-66', 0, None]

    result = search_phones(sample_df, '01.08.2025', '31.08.2025')
    data = json.loads(result)
    assert len(data) >= 1
    assert any('+7 999 88-77-66' in op['Описание'] for op in data)


def test_text_search(sample_df):
    result = text_search(sample_df, 'пятерочка')
    data = json.loads(result)
    assert len(data) == 1
    assert data[0]['Описание'] == 'Пятерочка'

    result_empty = text_search(sample_df, 'несуществующее_слово')
    assert result_empty == '[\n\n]'


def test_transfer_search(sample_df):
    result = transfer_search(sample_df)
    data = json.loads(result)
    assert len(data) >= 1
    desc = data[0]['Описание']
    assert 'Иванов' in desc or 'И.И.' in desc