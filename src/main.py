from api.hh_api import HHAPI
from database.db_creator import DBCreator
from database.db_manager import DBManager


def main():
    """Основная функция программы."""
    print("=== Парсер вакансий с HH.ru ===")

    # Создаем базу данных и таблицы
    db_creator = DBCreator()
    db_creator.create_database()
    db_creator.create_tables()

    # Инициализируем API и менеджер БД
    hh_api = HHAPI()
    db_manager = DBManager()

    # Список компаний для парсинга
    companies = [
        "Яндекс",
        "Сбер",
        "Тинькофф",
        "VK",
        "Ozon",
        "Лаборатория Касперского",
        "1С",
        "Ростелеком",
        "МТС",
        "Билайн"
    ]

    print("\nПолучаем данные о компаниях...")
    employers_data = []

    for company in companies:
        employers = hh_api.get_employers(company, per_page=1)
        if employers:
            employer_detail = hh_api.get_employer_details(employers[0]["id"])
            if employer_detail:
                employers_data.append(employer_detail)
                print(f"✓ {employer_detail['name']}")

    # Сохраняем работодателей в БД
    print("\nСохраняем данные в базу данных...")
    for employer in employers_data:
        db_manager.insert_employer(employer)

        # Получаем вакансии для каждого работодателя
        vacancies = hh_api.get_vacancies_by_employer(employer["id"])
        for vacancy in vacancies:
            db_manager.insert_vacancy(vacancy, employer["id"])

        print(f"✓ Сохранено {len(vacancies)} вакансий для {employer['name']}")

    # Взаимодействие с пользователем
    user_interface(db_manager)


def user_interface(db_manager: DBManager) -> None:
    """Интерфейс взаимодействия с пользователем."""
    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ:")
        print("1. Показать компании и количество вакансий")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("\nВыберите пункт меню: ").strip()

        if choice == "1":
            companies = db_manager.get_companies_and_vacancies_count()
            print("\nКомпании и количество вакансий:")
            print("-" * 40)
            for company in companies:
                print(f"{company['company']}: {company['vacancies_count']} вакансий")

        elif choice == "2":
            vacancies = db_manager.get_all_vacancies()
            print("\nВсе вакансии:")
            print("-" * 60)
            for vac in vacancies:
                print(f"{vac['company']} - {vac['vacancy']}")
                print(f"Зарплата: {vac['salary']}")
                print(f"Ссылка: {vac['url']}")
                print()

        elif choice == "3":
            avg_salary = db_manager.get_avg_salary()
            print(f"\nСредняя зарплата по всем вакансиям: {avg_salary:.2f} руб.")

        elif choice == "4":
            vacancies = db_manager.get_vacancies_with_higher_salary()
            print("\nВакансии с зарплатой выше средней:")
            print("-" * 60)
            for vac in vacancies:
                print(f"{vac['company']} - {vac['vacancy']}")
                print(f"Зарплата: {vac['salary']}")
                print(f"Ссылка: {vac['url']}")
                print()

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ").strip()
            if keyword:
                vacancies = db_manager.get_vacancies_with_keyword(keyword)
                print(f"\nРезультаты поиска по '{keyword}':")
                print("-" * 60)
                for vac in vacancies:
                    print(f"{vac['company']} - {vac['vacancy']}")
                    print(f"Зарплата: {vac['salary']}")
                    print(f"Ссылка: {vac['url']}")
                    print()
            else:
                print("Ключевое слово не может быть пустым!")

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Попробуйте еще раз.")


if __name__ == "__main__":
    main()
