from typing import Any, Dict, List, Optional

import psycopg2

from utils_local.config import config


class DBManager:
    """Класс для управления базой данных вакансий"""

    def __init__(self, db_name: str = "hh_vacancies"):
        self.params = config()
        self.params["database"] = db_name

    def execute_query(
        self, query: str, params: Optional[tuple[Any, ...]] = None, fetch: bool = True
    ) -> List[tuple[Any, ...]]:
        """Выполнить SQL запрос"""
        conn = None
        try:
            conn = psycopg2.connect(**self.params)
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Ошибка при выполнении запроса: {error}")
        finally:
            if conn:
                conn.close()
        return []

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """Получить список всех компаний и количество вакансий у каждой компании"""
        query = """
            SELECT e.name, COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.employer_id, e.name
            ORDER BY vacancies_count DESC
        """
        result = self.execute_query(query)
        return (
            [{"company": row[0], "vacancies_count": row[1]} for row in result]
            if result
            else []
        )

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """Получить список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию"""
        query = """
        SELECT e.name as company_name, v.name as vacancy_name, v.salary_from, v.salary_to, v.currency, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.employer_id
        ORDER BY e.name, v.name
        """
        result = self.execute_query(query)
        vacancies = []
        for row in result:
            salary = f"{row[2] or '?'}-{row[3] or '?'} {row[4] or ''}".strip()
            vacancies.append(
                {"company": row[0], "vacancy": row[1], "salary": salary, "url": row[5]}
            )
        return vacancies

    def get_avg_salary(self) -> float:
        """Получить среднюю зарплату по вакансиям"""
        query = """
        SELECT AVG((COALESCE(salary_from, 0) + COALESCE(salary_to, 0)) / 2) as avg_salary
        FROM vacancies
        WHERE salary_from IS NOT NULL OR salary_to IS NOT NULL
        """
        result = self.execute_query(query)
        return round(result[0][0], 2) if result and result[0][0] else 0.0

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """Получить список всех вакансий, у которых зарплата выше средней по всем вакансиям"""
        avg_salary = self.get_avg_salary()
        query = """
            SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 > %s
            ORDER BY (COALESCE(v.salary_from, 0) + COALESCE(v.salary_to, 0)) / 2 DESC
        """
        result = self.execute_query(query, (avg_salary,))
        vacancies = []
        for row in result:
            salary = f"{row[2] or '?'}-{row[3] or '?'} {row[4] or ''}".strip()
            vacancies.append(
                {"company": row[0], "vacancy": row[1], "salary": salary, "url": row[5]}
            )
        return vacancies

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """Получить список всех вакансий, в названии которых содержатся переданные слова"""
        query = """
            SELECT e.name, v.name, v.salary_from, v.salary_to, v.currency, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(v.name) LIKE %s
            ORDER BY e.name, v.name
        """
        result = self.execute_query(query, (f"%{keyword.lower()}%",))
        vacancies = []
        for row in result:
            salary = f"{row[2] or '?'}-{row[3] or '?'} {row[4] or ''}".strip()
            vacancies.append(
                {"company": row[0], "vacancy": row[1], "salary": salary, "url": row[5]}
            )
        return vacancies

    def insert_employer(self, employer_data: Dict[str, Any]) -> None:
        """Вставить данные работодателя в БД"""
        query = """
            INSERT INTO employers (hh_id, name, url, website_url, description, open_vacancies)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (hh_id) DO NOTHING
        """
        self.execute_query(
            query,
            (
                employer_data["id"],
                employer_data["name"],
                employer_data.get("alternate_url"),
                employer_data.get("site_url"),
                employer_data.get("description", "")[:1000],  # Ограничиваем длину
                employer_data.get("open_vacancies", 0),
            ),
            fetch=False,
        )

    def insert_vacancy(self, vacancy_data: Dict[str, Any], employer_hh_id: int) -> None:
        """Вставить данные вакансии в БД"""
        query = "SELECT employer_id FROM employers WHERE hh_id = %s"
        result = self.execute_query(query, (employer_hh_id,))

        if not result:
            print(f"Работодатель с hh_id={employer_hh_id} не найден в БД")
            return

        employer_id = result[0][0]

        salary = vacancy_data.get("salary", {}) or {}
        snippet = vacancy_data.get("snippet", {}) or {}

        query = """
        INSERT INTO vacancies (hh_id, employer_id, name, salary_from, salary_to, currency, url,
        requirement, responsibility, experience, employment_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (hh_id) DO NOTHING
        """

        # Безопасное получение значений
        requirement = snippet.get("requirement")
        responsibility = snippet.get("responsibility")

        self.execute_query(
            query,
            (
                vacancy_data["id"],
                employer_id,
                vacancy_data["name"],
                salary.get("from"),
                salary.get("to"),
                salary.get("currency"),
                vacancy_data.get("alternate_url", ""),
                requirement[:1000] if requirement else "",
                responsibility[:1000] if responsibility else "",
                vacancy_data.get("experience", {}).get("name"),
                vacancy_data.get("employment", {}).get("name"),
            ),
            fetch=False,
        )
