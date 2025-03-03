# RoboControl\services\common_utils.py
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException,
)
import pygetwindow as gw
import time
from settings.logger import setup_logger


logger = setup_logger(__name__)


def find_eds_file(folder_path: str) -> str:
    """
    Ищет файл в папке, имя которого начинается с 'AUTH_RSA256' или 'GOST512'.
    Возвращает полный путь к найденному файлу или None, если файл не найден.
    """
    try:
        logger.info(f"[SEARCH] Поиск файлов в папке: {folder_path}")
        
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                if file_name.startswith("AUTH_RSA256") or file_name.startswith("GOST512"):
                    logger.info(f"[FOUND] Найден файл: {file_path}")
                    return file_path
        logger.info(f"[NOT FOUND] Файлы с нужным названием не найдены в папке: {folder_path}")
        return None
    except FileNotFoundError:
        logger.error(f"[ERROR] Папка '{folder_path}' не найдена.")
    except PermissionError:
        logger.error(f"[ERROR] Нет доступа к папке '{folder_path}'.")
    except Exception as Err:
        logger.error(f"[ERROR] Ошибка при поиске EDS файла в {folder_path}: {Err}")
    return None

def extract_password_from_folder_name(folder_name: str) -> str:
    """
    Извлекает пароль из имени папки.
    Считается, что пароль всегда является последним элементом в имени папки, разделенным пробелами.
    
    :param folder_name: Имя папки.
    :return: Извлеченный пароль.
    """
    try:
        logger.info(f"[PROCESS] Извлечение пароля из имени папки: {folder_name}")
        
        parts = folder_name.split()
        if not parts:
            raise ValueError(f"Папка '{folder_name}' имеет некорректный формат (пустое имя).")
        
        password = parts[-1]
        logger.info(f"[EXTRACTED] Извлечен пароль: {password}")
        return password
    except ValueError as vErr:
        logger.error(f"[ERROR] Некорректное имя папки: {folder_name}. Ошибка: {vErr}")
    except Exception as Err:
        logger.error(f"[ERROR] Ошибка при извлечении пароля из имени папки '{folder_name}': {Err}")
        raise

def wait_for_window(title: str, timeout: int = 20):
    """
    Ожидает появления окна с указанным заголовком.

    :param title: Заголовок окна, который нужно найти.
    :param timeout: Максимальное время ожидания (в секундах).
    :return: Объект окна, если найдено, иначе None.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            return windows[0]
        time.sleep(0.1) 
    return None

def close_eds_window(window_title='Открыть файл'):
    """Закрыть окно выбора ЭЦП по его заголовку."""
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            window = windows[0]
            logger.info(f"[CLOSE EDS WINDOW] Окно с заголовком '{window_title}' найдено.")
            window.close()
            logger.info(f"[CLOSE EDS WINDOW] Окно с заголовком '{window_title}' закрыто.")
        else:
            logger.info(f"[CLOSE EDS WINDOW] Окно с заголовком '{window_title}' не найдено.")
    except Exception as Err:
        logger.error(f"[CLOSE EDS WINDOW ERROR] Ошибка при закрытии окна: {Err}")

def find_eds_file_and_password(selected_path):
    """Найти файл ЭЦП и извлечь пароль из имени папки"""
    for subdir in os.listdir(selected_path):
        logger.info(f'subdir={subdir}')
        subdir_path = os.path.join(selected_path, subdir)
        
        if os.path.isdir(subdir_path):
            # Находит файл EDS с именем "AUTH_RSA256" или "GOST512"
            eds_file = find_eds_file(subdir_path)
            logger.debug(f'[AUTH FIND FILE] Найденный файл с именем={eds_file}')

            if eds_file:
                # Если файл найден, извлекаем пароль из имени папки
                password = extract_password_from_folder_name(subdir)
                logger.debug(f'[AUTH EXTRACT PASSWORD] Извлеченный пароль={password[:2]}***')
                return eds_file, password
    return None, None

def escape_xpath_text(text):
    """Экранировать текст для безопасного использования в XPath."""
    if '"' in text:
        return "concat('{}')".format(text.replace("'", "', \"'\", '"))
    return f'"{text}"'
