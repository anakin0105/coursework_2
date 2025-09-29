import logging
import json
from datetime import datetime
import pandas as pd
from typing import Dict, Any
from utils import greeting  # Импортируем функцию greeting из utils.py

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
def home_page(date_str: str) -> str:
    logging.info("Формирование ответа для страницы 'Главная' с датой: %s", date_str)

    try:
        date_ = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        logging.error("Неверный формат даты: %s", date_str)
        raise ValueError("Ожидается формат 'YYYY-MM-DD HH:MM:SS'") from e

    # Получаем приветствие
    greeting_message = greeting(date_)

# Создаем объект datetime с текущей или произвольной датой и временем
date_ = datetime(2025, 9, 29, 4, 38, 0)  # Пример: 29 сентября 2025, 14:38

# Получаем приветствие
greeting_message = greeting(date_)

# Выводим результат
print(greeting_message)