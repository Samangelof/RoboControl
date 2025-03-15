from settings.logger import setup_logger
from selenium.webdriver.common.by import By
from core.services.robot_dependencies.selenium_scripts import WINDOW_ACTIVITY_SCRIPT
from core.services.utils.common_utils import (
    find_eds_file,
    extract_password_from_folder_name,
)
import os
import json

logger = setup_logger(__name__)

def check_navigation_proccess(driver):
        """Начать навигацию."""
        try:
            driver.navigate_to_url(url = 'https://cabinet.kgd.gov.kz/knp/main/index')
            driver.execute_script(WINDOW_ACTIVITY_SCRIPT)
            logger.info("[START OPEN URL] Открыл сайт: cabinet.kgd.gov.kz")
            
            driver.click_element(By.XPATH, "//a[contains(text(), 'Русский')]", "[START SETUP LANG RU] Установка языка на сайте 'Русский'")
            driver.click_element(By.XPATH, "//button[contains(text(), 'Войти по ЭЦП')]", "[START CLICK ELEMENT LOGIN EDS] 'Войти по ЭЦП'", wait_for_visibility=True)
        except Exception as Err:
            logger.error(f"[START CLASS ROBOT] Ошибка при выполнении start_navigation: {Err}")
            raise


def check_authenticate_proccess(driver, selected_path):
    logger.debug(f'path_in_auth={selected_path}')
    """Выполнить авторизацию."""
    try:
        # Основной цикл
        for subdir in os.listdir(selected_path):
            logger.info(f'subdir={subdir}')
            subdir_path = os.path.join(selected_path, subdir)
            
            if os.path.isdir(subdir_path):
                # Находим файл EDS с именем "AUTH_RSA256" или "GOST512"
                eds_file = find_eds_file(subdir_path)
                logger.debug(f'[AUTH FIND FILE] Найденный файл с именем={eds_file}')

                if eds_file:
                    # Если файл найден, извлекаем пароль из имени папки
                    password = extract_password_from_folder_name(subdir)
                    logger.debug(f'[AUTH EXTRACT PASSWORD] Извлеченный пароль={password[:2]}***')

                    # Авторизуем пользователя
                    file_input = driver.find_element(By.XPATH, "//input[@class='custom-file-input']")
                    driver.execute_script("arguments[0].style.display = 'block';", file_input)
                    file_input.send_keys(eds_file)
                    logger.debug(f"[AUTH SELECT FILE] Файл выбран: {eds_file}")
                    password_field = driver.find_element(By.XPATH, "//input[@type='password' and @class='listBox form-control' and not(@disabled)]")
                    password_field.clear()
                    password_field.send_keys(password)
                    driver.click_element(By.XPATH, "//button[contains(text(), 'Ok') and not(@disabled)]", "[AUTH CLICK ELEMENT 'OK'] Нажата кнопка 'Ok'")
                    button_xpath = "//button[contains(@class, 'btn-secondary') and contains(text(), 'Данные о сертификате')]"

                    logger.info(f"[WAIT] Ожидание кнопки 'Данные о сертификате' в течение 1 секунды")

                    # Используем встроенный метод wait_for_element
                    if driver.wait_for_element(By.XPATH, button_xpath, timeout=1):
                        logger.info("[SUCCESS] Кнопка 'Данные о сертификате' найдена.")
                        continue
                    else:
                        logger.warning(f"[TIMEOUT] Кнопка 'Данные о сертификате' не найдена за 1 секунду.")
                    # Проверяем появление ошибок
                        alert = driver.find_element(By.XPATH, "//div[contains(@class, 'alert-danger')]", wait_time=2)

                        if alert:
                            alert_text = alert.text.strip() if alert.text else ""

                            if "Срок действия Вашего сертификата" in alert_text:
                                logger.warning(f"[AUTH SKIP] Сертификат в {subdir} истек, пропускаем.")
                                error_data = {
                                    "error": "Срок действия Сертификата истек!",
                                    "eds_file": os.path.basename(os.path.dirname(eds_file)) # Записываем только папку файла ЭЦП
                                }
                                if is_certificate_in_json(error_data):
                                    continue
                                else:
                                    append_element_to_json(error_data, json_file="error_log.json")
                                    continue

                            if "Введите верный пароль" in alert_text:
                                logger.warning(f"[AUTH SKIP] Неверный пароль для {subdir}, пропускаем.")
                                error_data = {
                                    "error": "Неверный пароль",
                                    "eds_file": os.path.basename(os.path.dirname(eds_file)) # Записываем только папку файла ЭЦП
                                }

                                if is_certificate_in_json(error_data):
                                    continue
                                else:
                                    append_element_to_json(error_data, json_file="error_log.json")
                                    continue
                        else:
                            logger.debug(f"[AUTH CHECK] Ошибок не обнаружено для {subdir}, продолжаем.")

                    driver.click_element(By.XPATH, "//button[contains(text(), 'Выбрать')]", "[AUTH CLICK ELEMENT 'SELECT'] Нажата кнопка 'Выбрать'")
    except Exception as Err:
        logger.error(f"[CLASS ROBOT] Ошибка при выполнении authenticate: {Err}")
        raise

def clear_json_file(json_file="error_log.json"):
    """
    Очищает JSON-файл перед записью новых ошибок.
    """
    try:
        with open(json_file, "w", encoding="utf-8") as file:
            json.dump([], file, indent=4, ensure_ascii=False)  # Создаём пустой список
        logger.info(f"[JSON CLEAR] Файл {json_file} очищен перед началом записи.")
    except Exception as e:
        logger.error(f"[ERROR JSON] Ошибка при очистке JSON-файла: {e}")


def append_element_to_json(error_data, json_file):
    """
    Добавляет новую ошибку в JSON-файл, если он существует.

    :param error_data: Словарь с данными об ошибке
    :param json_file: Путь к JSON-файлу
    """
    try:
        if os.path.exists(json_file):
            with open(json_file, "r+", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    if not isinstance(data, list):
                        data = []  # Если файл поврежден, создаём пустой список
                except json.JSONDecodeError:
                    data = []  # Если файл пуст или битый

                # Добавляем новую ошибку
                data.append(error_data)

                # Перезаписываем JSON без создания нового файла
                file.seek(0)
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.truncate()

            logger.info(f"[JSON LOG] Сохранено в файл {json_file}")
        else:
            logger.warning(f"[JSON LOG] Файл {json_file} отсутствует. НЕ записано.")

    except Exception as e:
        logger.error(f"[ERROR JSON] Ошибка при записи в JSON-файл: {e}")



def is_certificate_in_json(error_data, json_file="error_log.json"):
    """
    Проверяет, есть ли уже такой сертификат в JSON.

    :param error_data: Данные об ошибке {"error": "...", "eds_file": "..."}
    :param json_file: Путь к JSON-файлу
    :return: True, если сертификат уже есть, иначе False
    """
    if not os.path.exists(json_file):
        return False

    try:
        with open(json_file, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if not isinstance(data, list):
                    return False  # JSON не в ожидаемом формате
            except json.JSONDecodeError:
                return False  # Если файл пуст или битый

        # Проверяем, есть ли уже такой сертификат
        for entry in data:
            if entry["eds_file"] == error_data["eds_file"]:
                return True

    except Exception as e:
        logger.error(f"[ERROR JSON] Ошибка при проверке сертификата в JSON: {e}")

    return False