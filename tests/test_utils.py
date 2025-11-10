from datetime import datetime
from unittest.mock import patch
from src.utils import greeting  # ← подправь путь, если нужно

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

def test_logging():
    with patch('logging.info') as mock_info:
        greeting(datetime(2025, 1, 1, 10, 0))
        mock_info.assert_called_once_with("Обработка времени: %s", datetime(2025, 1, 1, 10, 0))