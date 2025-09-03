import requests
from typing import Dict, List, Any, Optional


class HHAPI:
    """ Класс для работы с API HeadHunter """
    BASE_URL = "https://api.hh.ru/"
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "HH_API-Client/1.0"})

    def get_employers(self, search_query: str, area: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """ Получает список работодателей по поисковому запросу """
        url = f"{self.BASE_URL}employers"
        params = {
            "text": search_query,
            "area": area,
            "only_with_vacancies": True,
            "per_page": per_page
        }
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()["items"]
        except requests.RequestException as e:
            print(f"Ошибка при получении данных работодателей: {e} ")
            return []

    def get_vacancies_by_employer(self, employer_id: str) -> List[Dict[str, Any]]:
        """ Получает вакансии конкретного работодателя """
        url = f"{self.BASE_URL}vacancies"
        params = {
            "employer_id": employer_id,
            "per_page": 100
        }
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()['items']
        except requests.RequestException as e:
            print(f"Ошибка при получении вакансий для работодателя {employer_id}: {e}")
            return []

    def get_employer_details(self, employer_id: str) -> Optional[Dict[str, Any]]:
        """ Получает детальную информацию о работодателе """
        url = f"{self.BASE_URL}employers/{employer_id}"

        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении информации о работодателе {employer_id}: {e}")
            return None

