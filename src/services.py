from typing import List, Dict


def cashback_categories(year: int, month: int, transactions: List[Dict]) -> Dict:
    """ Анализирует кешбэк по категориям за указанный месяц и год. Принимает список транзакций (словари).
  Возвращает JSON {категория: сумма_кешбэка}. Использует json, datetime, logging.
  """
pass

def investment_bank(month: str, transactions: List[Dict], limit: int) -> float:
    """Рассчитывает сумму для "Инвесткопилки" за месяц (YYYY-MM). Округляет расходы до limit (10/50/100). Возвращает сумму округлений.
  Использует json, datetime, logging.
  """
pass

def simple_search(query: str, transactions: List[Dict]) -> List[Dict]:
    """Ищет транзакции, где строка query есть в описании или категории. Возвращает JSON-список транзакций. Использует json, logging.
  """
pass

def search_phone_numbers(transactions: List[Dict]) -> List[Dict]:
    """Ищет транзакции с мобильными номерами в описании (формат: +7 xxx xx-xx-xx). Возвращает JSON-список транзакций. Использует json, re, logging.
  """
pass

def search_transfers_to_individuals(transactions: List[Dict]) -> List[Dict]:
    """Ищет переводы физлицам (категория "Переводы", описание вида "Имя Ф."). Возвращает JSON-список транзакций. Использует json, re, logging.
  """
pass