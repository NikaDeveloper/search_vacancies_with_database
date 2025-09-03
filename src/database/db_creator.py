import psycopg2
from utils.config import config


class DBCreator:
    """ Класс для создания базы данных и таблиц """
    def __init__(self, db_name: str = "hh_vacancies"):
        self.db_name = db_name
        self.params = config()

    def create_database(self) -> None:
        """ Создать базу данных """
        conn = None
        try:
            params = self.params.copy()
            params.pop("database", None)

            conn = psycopg2.connect(**params)
            conn.autocommit = True
            cursor = conn.cursor()

            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.db_name}'")
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {self.db_name}")
                print(f"База данных {self.db_name} создана успешно")
            else:
                print(f"База данных {self.db_name} уже существует")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Ошибка при создании базы данных: {error}")
        finally:
            if conn:
                conn.close()

    def create_tables(self) -> None:
        """ Создать таблицы в базе данных """
        commands = (
            """
                        CREATE TABLE IF NOT EXISTS employers (
                            employer_id SERIAL PRIMARY KEY,
                            hh_id INTEGER UNIQUE NOT NULL,
                            name VARCHAR(255) NOT NULL,
                            url VARCHAR(255),
                            website_url VARCHAR(255),
                            description TEXT,
                            open_vacancies INTEGER
                        )
                        """,
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                vacancy_id SERIAL PRIMARY KEY,
                hh_id INTEGER UNIQUE NOT NULL,
                employer_id INTEGER REFERENCES employers(employer_id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                currency VARCHAR(10),
                url VARCHAR(255) NOT NULL,
                requirement TEXT,
                responsibility TEXT,
                experience VARCHAR(100),
                employment_type VARCHAR(100)
            )
            """
        )

        conn = None
        try:
            params = self.params.copy()
            params["database"] = self.db_name

            conn = psycopg2.connect(**params)
            cursor = conn.cursor()

            for command in commands:
                cursor.execute(command)

            conn.commit()
            print("Таблицы созданы успешно")

        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Ошибка при создании таблиц: {error}")
            raise
        finally:
            if conn:
                conn.close()

