import os
import logging
from datetime import datetime
from src.utils import read_excel
from src.services import top_cashback_categories, search_phones,investment_bank, transfer_search, text_search
from src.reports import spending_by_weekday, spending_by_catеgory,spending_by_workday
from src.views import home_page


# ЛОГИРОВАНИЕ
logger = logging.getLogger('Main_logger')
logger.setLevel(logging.DEBUG)
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
log_name = datetime.today().strftime("%Y-%m-%d %H-%M-%S") + ".log"
log_file = os.path.join(log_dir, log_name)
file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s","%Y-%m-%d %H:%M:%S")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def services():
    while 1:
        sers = {1: "Категории повышенного кэшбека", 2: "Инвесткопилка", 3: "Простой поиск", 4: "Поиск по телефону",
                5: "Поиск по людям", 0: "Возврат в главное меню"}
        print("\nСервисы\nВыберите нужный сервис")
        for k, v in sers.items():
            print(f"\t{k}: {v}")
        s = input("Введите команду: ")
        if s == "1":
            top_cashback_categories(data, 2025, 8)
        elif s == "2":
            investment_bank('08.2025', data, 50)
        elif s == "3":
            text_search(data, "МТС")
        elif s == "4":
            search_phones(data, '01.08.2025','08.08.2025')
        elif s == "5":
            transfer_search(data,'18.08.2025','30.08.2025')
        elif s == '0':
            print('- Возвращаюсь в главное меню')
            return 1
        else:
            print("Команда не распознана, введите, пожалуйста, одну из команд из списка")
            continue


def reports():
    while 1:
        reps = {1: "Траты по категории", 2: "Траты по дням недели", 3: "Траты в рабочий/выходной день",
                0: "Возврат в главное меню"}
        print("\nОтчеты\nВыберите нужный отчет")
        for k, v in reps.items():
            print(f"\t{k}: {v}")
        r = input("Введите команду: ")
        if r == "1":
            spending_by_catеgory(data,"Экосистема Яндекс")
        elif r == "2":
            spending_by_weekday(data)
        elif r == "3":
            spending_by_workday(data)
        elif r == '0':
            print('- Возвращаюсь в главное меню')
            return 1
        else:
            print("Команда не распознана, введите, пожалуйста, одну из команд из списка")
            continue


def main():
    """
        Основная функция – точка входа в приложение.
        Запускает бесконечный цикл главного меню, пока пользователь не выберет «Выход».
        """
    actions = {1: "Главная страница", 2: "Страница событий (В РАЗРАБОТКЕ)", 3: "Сервисы", 4: "Отчеты", 0: "Выход"}
    while 1:
        back = 0
        print(
            '\nДобро пожаловать в банковское приложение "BestBank". \nДля продолжения работы выберите один из вариантов')
        for k, v in actions.items():
            print(f"\t{k}: {v}")
        page = input("Введите команду: ")

        if page == "1":
            home_page(data, logger)
        elif page == "2":
            print("Страница событий(В РАЗРАБОТКЕ)")
        elif page == "3":
            back = services()
        elif page == "4":
            back = reports()
        elif page == "0":
            print('Спасибо за выбор нашего банка, хорошего дня!')
            break
        else:
            print("Команда не распознана, введите, пожалуйста, одну из команд из списка")
            continue

        if back:
            continue
        else:
            print('- Введите 0 для выхода из программы, при ином вводе возврат к выбору вариантов')
            back = input()
            if back != "0":
                print('- Возвращаюсь в главное меню')
                # os.system('clear')
                continue
            else:
                print('Спасибо за выбор нашего банка, хорошего дня!')
                break

if __name__ == "__main__":
    data = read_excel("1.xls")
    main()
