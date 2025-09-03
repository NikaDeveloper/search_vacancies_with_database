import requests

# ID работодателя (например, Яндекс)
employer_id = '1740'

# Формируем URL. Говорим: "Дайте мне вакансии для работодателя с ID 1740"
url = f'https://api.hh.ru/vacancies?employer_id={employer_id}&per_page=20'

# Делаем запрос
response = requests.get(url)
vacancies_data = response.json()

print(f"Вакансии компании: {vacancies_data['items'][0]['employer']['name']}")
print("----------------------------------------")

# Выводим список вакансий
for vacancy in vacancies_data['items']:
    print(f"Должность: {vacancy['name']}")
    print(f"Зарплата: {vacancy['salary']}")  # Может быть None, если не указана
    print(f"Требования: {vacancy['snippet']['requirement']}")
    print(f"Ссылка: {vacancy['alternate_url']}")
    print("---")
