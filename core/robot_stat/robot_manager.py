# core/robot_stat/robot_manager.py
import time 
import json
import asyncio
import os
from pywinauto import Application
import pyautogui
import pyperclip
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from core.services.robot_dependencies.selenium_scripts import WINDOW_ACTIVITY_SCRIPT
from selenium.webdriver.common.by import By
from core.services.utils.common_utils import (
    wait_for_window,
    find_eds_file,
    extract_password_from_folder_name,
)
from core.robot_stat.robot_checker import (
    check_navigation_proccess,
    check_authenticate_proccess,
    clear_json_file,
    append_element_to_json
)
from settings.logger import setup_logger
from core.base_robot import BaseRobot


logger = setup_logger(__name__)


class RobotStat(BaseRobot):
    STAT_URL = 'https://cabinet.stat.gov.kz/'
    def check_certificates(self, selected_path):
        clear_json_file(json_file="error_log.json")
        clear_json_file(json_file="reports.json")
        check_navigation_proccess(self.driver)
        check_authenticate_proccess(self.driver, selected_path)

    def navigation_proccess(self):
        """Выполнить навигацию"""
        try:
            self.driver.navigate_to_url(self.STAT_URL)
            
            self.driver.execute_script(WINDOW_ACTIVITY_SCRIPT)
            logger.info("[START OPEN URL] Открыл сайт: cabinet.stat.gov.kz")
            
            self.driver.click_element(By.XPATH, '//a[@id="idLogin" and @href="#" and text()="Войти"]')

            self.driver.click_element(By.XPATH, '//div[@id="container-1076-innerCt"]//span[@id="button-1077-btnInnerEl" and text()="Согласен"]')

            self.driver.click_element(By.XPATH, '//input[@type="checkbox" and @name="lawAlertCheck" and @id="lawAlertCheck"]')

            self.driver.click_element(By.XPATH, '//input[@type="submit" and @id="loginButton" and @value="Войти в систему"]', wait_for_visibility=True)

        except Exception as Err:
            logger.error(f"[START CLASS ROBOT] Ошибка при выполнении start_navigation: {Err}")
            self.driver.quit()
            raise

    def authenticate_proccess(self, selected_path):
        """Выполнить авторизацию"""
        count = 0 # Счётчик проверенных эцп
        logger.debug(f'path_in_auth={selected_path}')

        try:
            # self.state = RobotState.AUTH_STARTED
            # logger.info(f"[AUTH STATE CHANGE] Состояние изменено: {self.state.value}")
            for subdir in os.listdir(selected_path):
                logger.info(f'subdir={subdir}')
                subdir_path = os.path.join(selected_path, subdir)
                if os.path.isdir(subdir_path):
                    # Получаю файл ЭЦП и пароль
                    eds_file = find_eds_file(subdir_path)
                    if is_certificate_in_json({"eds_file": os.path.basename(os.path.dirname(eds_file))}, "error_log.json"): # Проверка на корректность сертификата
                        logger.debug("[AUTH ERROR] Ошибка сертификата! Пропускаем...")
                        continue
                    password = extract_password_from_folder_name(subdir)
                    logger.debug(f'[AUTH FIND FILE] Найденный файл с именем={eds_file}')
                    if eds_file and password:
                        if count >= 1:
                            self.navigation_proccess() # Повторная навигация для следующих ЭЦП
                        authorize_face(eds_file, password)
                        self.reports_proccess()
                        self.logout_process()
                        count += 1
                else:
                    logger.error("[AUTH ERROR] Файл ЭЦП или пароль не найдены")
        
        except Exception as e:
            logger.error(f"[AUTH ERROR] Произошла ошибка при авторизации: {e}")

    def reports_proccess(self):
        reports_tab_xpath = "//span[@id='tab-1168-btnInnerEl' and contains(text(), 'Мои отчёты')]"
        if not self.driver.wait_for_element(By.XPATH, reports_tab_xpath, timeout=5):
            logger.warning(f"[TIMEOUT] Вкладка 'Мои отчёты' не найдена за 5 секунд.")
            return False

        # Кликаем по вкладке
        self.driver.click_element(By.XPATH, reports_tab_xpath, log_message="Клик по вкладке 'Мои отчёты'")
        logger.info("[REPORTS] Навигация на отчёты была выполнена успешно")

        # ИСПРАВЛЕНО: Используем `find_elements()`, а не `wait_for_element()`
        report_rows = self.driver.find_elements(By.XPATH, "//tr[contains(@class, 'x-grid-data-row')]")

        # Проверяем, что найдены строки
        if not report_rows:
            logger.warning("[REPORTS] Строки с отчетами не найдены.")
            return False

        # Название компании
        company_name_element = self.driver.find_element(By.ID, "tab_header_hd-textEl")
        company_name = company_name_element.text.strip()
        logger.info("[REPORTS] Название компании было скопировано успешно")

        for row in report_rows:
            try:
                # Извлекаем данные
                report_form_element = row.find_element(By.XPATH, ".//td[contains(@class, 'x-grid-cell-gridcolumn-1143')]")
                report_form = report_form_element.text.strip()
                logger.info("[REPORTS] Форма была скопирована успешно")

                report_start_date_element = row.find_element(By.XPATH, ".//td[contains(@class, 'x-grid-cell-gridcolumn-1146')]")
                report_start_date = report_start_date_element.text.strip()
                logger.info("[REPORTS] Дата начала была скопирована успешно")

                report_end_date_element = row.find_element(By.XPATH, ".//td[contains(@class, 'x-grid-cell-gridcolumn-1147')]")
                report_end_date = report_end_date_element.text.strip()
                logger.info("[REPORTS] Дата окончания была скопирована успешно")

                report_notes_element = row.find_element(By.XPATH, ".//td[contains(@class, 'x-grid-cell-gridcolumn-1148')]")
                report_notes = report_notes_element.text.strip()
                logger.info("[REPORTS] Примечание было скопировано успешно")

                report_status_element = row.find_element(By.XPATH, ".//td[contains(@class, 'x-grid-cell-gridcolumn-1149')]")
                report_status = report_status_element.text.strip()
                logger.info("[REPORTS] Статус был скопирован успешно")

                # Проверяем условия: если статус "Не сдан" и примечаний нет
                if report_status == "Не сдан" and report_notes in ["", " "]: 
                    report = {
                        "Название компании": company_name,
                        "Форма": report_form,
                        "Срок сдачи": f" от {report_start_date} до {report_end_date}",
                        "Статус": report_status
                    }
                    append_element_to_json(report, json_file="reports.json")

            except Exception as e:
                logger.error(f"Ошибка при обработке строки: {e}")


    
    def logout_process(self):
        self.driver.wait_for_element(By.XPATH, '//a[contains(@onclick, "onLogoutClick")]') # Ожидание кнопки выйти
        self.driver.click_element(By.XPATH, '//a[contains(@onclick, "onLogoutClick")]', log_message="Клик по кнопке выхода") # Нажатие на кноку выйти
        time.sleep(2)
    



def _activate_window_and_input(window_title, input_text, action_description):
    window = wait_for_window(window_title)
    if window:
        logger.debug(f'[AUTH] Активация окна: {window_title}')
        window.activate()
        pyperclip.copy(input_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(.3)
        pyautogui.press('enter')
        logger.debug(f'[AUTH SUCCESS] {action_description} выполнено успешно.')
        return True
    else:
        logger.debug(f'[AUTH WINDOW NOT FOUND] Окно "{window_title}" не найдено.')
        return False
    
def key_list_window(window_title, action_description):
    #todo: Марк: Добавил таймаут в 2с вместо 20с (дефолт)
    #todo: обернул в try-except
    #todo: Добавил sleep на случай, если робот будет слишком быстр
    try:
        window = wait_for_window(window_title, timeout=2)
        if window:
            logger.debug(f"[AUTH] Обработка окна: {window_title}")
            app = Application().connect(title=window_title)
            window = app.window(title=window_title)
            pyautogui.press("tab")
            time.sleep(.3)
            pyautogui.press("space")
            logger.debug(f'[AUTH SUCCESS] {action_description} выполнено успешно.')
            return True
        else:
            logger.debug(f'[AUTH WINDOW NOT FOUND] Окно "{window_title}" не найдено.')
            return False
    except Exception as e:
        logger.error(f'[AUTH ERROR] Неизвестная ошибка при обработке окна "{window_title}": {e}')
        return False




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








def authorize_face(file_to_path, file_password):
    try:
        logger.debug(f'[AUTH FACE SUCCESS] path={file_to_path}, password={file_password[:2]}***')
        # Step 0: Проверка на наличие окна списка ключей
        key_list_window("Список ключей", "Выбрать новый ключ")
        # Step 1: Активация окна для выбора ЭЦП
        if not _activate_window_and_input('Открыть файл', file_to_path, 'Копирование пути в буфер обмена'):
            raise Exception("Окно выбора файла не найдено")

        # Step 2: Ожидание окна ввода пароля
        if not _activate_window_and_input('Формирование ЭЦП в формате CMS', file_password, 'Ввод пароля'):
            raise Exception("Окно ввода пароля не найдено")

        # Step 3: Подтверждение подписи (только нажатие enter)
        window = wait_for_window('Формирование ЭЦП в формате CMS')
        if window:
            logger.debug('[AUTH PASSWORD WINDOW ACTIVATION] Окно подтверждения подписи найдено. Активация...')
            window.activate()
            time.sleep(.3)
            logger.debug('[AUTH SIGN ENTER] Нажатие Enter для подписи')
            pyautogui.press('enter')
            logger.debug('[AUTH SUCCESS] Подпись подтверждена.')
            

        else:
            logger.info('[AUTH PASSWORD WINDOW NOT FOUND] Окно для подписи не найдено в течение времени ожидания')

    
    except Exception as Err:
        logger.error(f'[AUTH FACE ERROR] Произошла ошибка при авторизации: {Err}')
        raise