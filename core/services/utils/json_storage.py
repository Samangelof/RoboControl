# RoboControl\services\json_storage.py
import json
import os
from settings.logger import setup_logger


logger = setup_logger(__name__)


# ==================================================================================================================================
# Загрузка конфигов
def load_config():
    """Загрузка сохраненного пути из JSON-файла."""
    try:
        with open("config.json", "r", encoding='utf-8') as json_file:
            data = json.load(json_file)
            path = data.get("path", None)
            if path:
                logger.info(f"[LOAD PATH] {path}")
                return path
            else:
                logger.info("[UNDEFINED PATH] Путь не найден в файле")
                return None
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("[LOAD CONFIG] Файл config.json не найден или содержит ошибки")
        return None
# ==================================================================================================================================


# ==================================================================================================================================
# Сохранить путь до директории с ЭЦП ключами
def save_path_to_json(directory):
    """Сохраняет путь в JSON."""
    try:
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump({'path': directory}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f'Ошибка при сохранении пути: {e}')
# ==================================================================================================================================


# ==================================================================================================================================
# сохранить данные о запуске робота
def save_run_data(run_data, file_path="statistics.json"):
    try:
        # Проверка, существует ли файл и не пустой ли он
        if os.path.exists(file_path) and os.stat(file_path).st_size > 0:
            with open(file_path, "r", encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = []  # Если файл пуст или не существует, начинаем с пустого списка

        # Логирование данных перед записью
        logger.info(f"[SAVE RUN DATA] Добавление данных в файл: {run_data}")

        data.append(run_data)

        with open(file_path, "w", encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        logger.info(f"[SAVE RUN DATA] Данные успешно сохранены в {file_path}")

    except Exception as e:
        logger.error(f"[ERROR SAVE RUN DATA] Ошибка при сохранении данных: {e}")
# ==================================================================================================================================
