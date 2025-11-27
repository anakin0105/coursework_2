import json
from typing import Dict
import pytest
#from openpyxl.styles.builtins import currency

#from src.services import top_cashback_categories
# Настройка логирования
import logging
import pandas as pd
from datetime import datetime, time

from src.views import home_page


@pytest.fixture
def sample_df():
    data = {
        'Дата операции': [
            '25.08.2025 10:30:00', '27.08.2025 14:20:00', '28.08.2025 09:15:00',
            '29.08.2025 12:00:00', '30.08.2025 18:45:00'
        ],
        'Статус': ['OK', 'OK', 'OK', 'OK', 'OK'],
        'Сумма операции': [-1500.0, -237.0, -890.0, -500.0, -320.0],
        'Кэшбэк': [75.0, 0, 44.5, 25.0, 0],
        'Категория': ['Переводы', 'Транспорт', 'Рестораны', 'Супермаркеты', 'Мобильная связь'],
        'Описание': [
            'Пятерочка', 'Яндекс Такси', 'Burger King', 'Магнит', 'Перевод Иванову И.И.'
        ],
        'Округление на инвесткопилку': [50, 13, 10, 0, 30],
        'Номер карты': ['123456****7890', '123456****7890', None, '123456****7890', '123456****7890']
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], dayfirst=True)
    return df



def test_home_page(sample_df):
    data = sample_df
    logger = logging.getLogger('Main_logger')
    logger.setLevel(logging.DEBUG)
    logger.info("Тестовый логер запущен. Все работает! Теперь без багов!")
    result = json.loads(home_page(data, logger))
    assert len(result) == 5