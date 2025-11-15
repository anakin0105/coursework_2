from datetime import datetime
from unittest.mock import patch

import requests_mock

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

