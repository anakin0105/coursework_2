from typing import Optional

import pandas as pd


def report_decorator(file_name: Optional[str] = None):
    """ Декоратор для функций отчетов. Записывает результат (JSON/DataFrame) в файл. Если file_name не указан,
  использует имя по умолчанию (например, "report_*.json"). Использует json.
  """
pass

def spending_by_category(df: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """ Возвращает траты по категории за 3 месяца от date (или текущей даты). Использует pandas, json, datetime, logging.
  """
pass

def spending_by_weekday(df: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """ Возвращает средние траты по дням недели за 3 месяца от date (или текущей даты). Использует pandas, json, datetime, logging.
  """
pass

def spending_by_workday(df: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """ Возвращает средние траты в рабочие и выходные дни за 3 месяца от date (или текущей даты). Использует pandas, json, datetime, logging.
  """
pass