from pathlib import Path
from dotenv import load_dotenv
import json
import pandas as pd
from datetime import datetime
import re






def app_main(current_date_str: str, transaction_file: str) -> None:
    """
    Принимает:
        current_date_str (str): Дата и время в формате 'DD.MM.YYYY HH:MM:SS'.
        transaction_file (str): Путь к Excel-файлу с транзакциями (например, 'Operations.xls').
    Выдает:
        None: Выводит JSON для главной страницы, список транзакций с телефонами и отчет по категории в консоль.

    Основная функция: генерирует отчеты по транзакциям из Excel-файла.
    """
    # Читаем Excel-файл, пропуская первую строку (заголовок "Отчет по операциям")
    print("\nЧитаю Excel-файл с транзакциями...")
    try:
        transactions = pd.read_excel(transaction_file, skiprows=1)
    except FileNotFoundError:
        print(f"Ошибка: файл {transaction_file} не найден")
        return

    # --- Главная страница ---
    # Парсим дату
    current_date = datetime.strptime(current_date_str, '%d.%m.%Y %H:%M:%S')
    start_date = current_date.replace(day=1, hour=0, minute=0, second=0)

    print("\nСтраница 'Главная'")
    print(f"Начало периода: {start_date}")
    print(f"Конец периода: {current_date}")

    # Фильтруем транзакции по датам, статусу OK и непустым номерам карт
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], dayfirst=True)
    filtered = transactions[
        (transactions['Дата операции'].between(start_date, current_date)) &
        (transactions['Статус'] == 'OK') &
        (transactions['Номер карты'].notna())
    ].fillna(0)

    # Приветствие
    hour = current_date.hour
    greeting_message = "Доброе утро" if hour < 12 else "Добрый день" if hour < 18 else "Добрый вечер" if hour < 23 else "Доброй ночи"

    # Расходы и кэшбэк по картам
    cards = filtered[filtered['Сумма операции'] < 0]['Номер карты'].unique()
    cards_expenses = []
    for card in cards:
        card_exp = filtered[(filtered['Номер карты'] == card) & (filtered['Сумма операции'] < 0)]
        total = round(abs(card_exp['Сумма операции'].sum()), 2)
        cashback = round(total / 100, 2)
        cards_expenses.append({
            'last_digits': str(card)[-4:],
            'total_spent': total,
            'cashback': cashback
        })

    # Топ-5 транзакций
    top_expenses = filtered[filtered['Сумма операции'] < 0][['Дата операции', 'Сумма операции', 'Категория', 'Описание']]
    top_expenses = top_expenses.sort_values(by='Сумма операции').head(5)
    top_transactions = [
        {
            'date': row['Дата операции'].strftime('%d.%m.%Y'),
            'amount': abs(row['Сумма операции']),
            'category': row['Категория'],
            'description': row['Описание']
        }
        for _, row in top_expenses.iterrows()
    ]

    # Заглушки для валют и акций (вместо API)
    currency_rates = [
        {"currency": "USD", "rate": 73.21},
        {"currency": "EUR", "rate": 87.08}
    ]
    stock_prices = [
        {"stock": "AAPL", "price": 150.12},
        {"stock": "AMZN", "price": 3173.18}
    ]

    # Формируем JSON для главной страницы
    main_page = {
        "greeting": greeting_message,
        "cards": cards_expenses,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    print("\nJSON для главной страницы:")
    print(json.dumps(main_page, ensure_ascii=False, indent=4))

    # --- Поиск транзакций с телефонными номерами ---
    pattern = re.compile(r'\d{3} \d{3}-\d{2}-\d{2}')
    phones = transactions[transactions['Описание'].str.contains(pattern, na=False)][['Дата операции', 'Сумма операции', 'Категория', 'Описание']].fillna(0)
    phones_json = json.dumps(phones.to_dict(orient='records'), ensure_ascii=False, indent=4)
    print("\nТранзакции с телефонными номерами:")
    print(phones_json)

    # --- Отчет по категории "Супермаркеты" за 3 месяца ---
    back_date = current_date - pd.Timedelta(days=90)
    category = 'Супермаркеты'
    cat_expenses = transactions[
        (transactions['Дата операции'].between(back_date, current_date)) &
        (transactions['Статус'] == 'OK') &
        (transactions['Категория'] == category)
    ]
    total = round(abs(cat_expenses['Сумма операции'].sum()), 2)
    print(f"\nТраты за 3 месяца в категории '{category}': {total} руб.")

# Запуск
if __name__ == '__main__':
    current_date = "30.12.2021 11:27:01"
    transaction_file = "operations.xls"  # Изменено на правильное имя файла
    app_main(current_date, transaction_file)
