import os
from configparser import ConfigParser
from typing import Any, Dict


def config(
    filename: str = "config/database.ini", section: str = "postgresql"
) -> Dict[str, Any]:
    """Чтение конфигурации базы данных из файла"""
    # Получаем абсолютный путь к файлу конфигурации
    base_dir = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    config_path = os.path.join(base_dir, filename)

    parser = ConfigParser()
    parser.read(config_path)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f"Секция {section} не найдена в файле {config_path}")

    return db
