import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)


def greeting(date_: datetime) -> str:
    """
    Возвращает приветствие в зависимости от времени суток на основе объекта datetime.

    Args:
        date_ (datetime): Объект datetime с датой и временем.

    Returns:
        str: Приветствие ('Доброе утро', 'Добрый день', 'Добрый вечер', 'Доброй ночи').
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