import time 
import os
import pygetwindow as gw
import pyautogui
import pyperclip
from core.services.robot_dependencies.selenium_driver import SeleniumDriver
from core.services.robot_dependencies.selenium_scripts import WINDOW_ACTIVITY_SCRIPT
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from core.robot_isna.robot_state import RobotState
from core.services.utils.common_utils import (
    extract_password_from_folder_name, 
    find_eds_file,
    wait_for_window,
    close_eds_window
)
from settings.logger import setup_logger
from core.base_robot import BaseRobot


logger = setup_logger(__name__)


class RobotKNP(BaseRobot):
    KNP_URL = 'https://cabinet.kgd.gov.kz/knp/main/index'
    BALANCE_PERSONAL_ACCOUNTS_URL = "https://cabinet.kgd.gov.kz/knp/p_accounts/card/"

    def navigation_proccess(self):
        """Начать навигацию."""
        try:
            self.state = RobotState.NAVIGATION_STARTED
            logger.info(f"[START STATE CHANGE] Состояние изменено: {self.state.value}")
            self.driver.navigate_to_url(self.KNP_URL)
            self.driver.execute_script(WINDOW_ACTIVITY_SCRIPT)
            logger.info("[START OPEN URL] Открыл сайт: cabinet.kgd.gov.kz")
            
            self.driver.click_element(By.XPATH, "//a[contains(text(), 'Русский')]", "[START SETUP LANG RU] Установка языка на сайте 'Русский'")
            self.driver.click_element(By.XPATH, "//button[contains(text(), 'Войти по ЭЦП')]", "[START CLICK ELEMENT LOGIN EDS] 'Войти по ЭЦП'", wait_for_visibility=True)
            self.state = RobotState.NAVIGATION_COMPLETED
            logger.info(f"[START STATE CHANGE] Состояние изменено: {self.state.value}")
        except Exception as Err:
            self.state = RobotState.ERROR
            logger.error(f"[START CLASS ROBOT] Ошибка при выполнении start_navigation: {Err}")
            self.driver.quit()
            raise
#! ПРИ ВХОДЕ В СИСТЕМУ 
#! И В СЛУЧАЕ ОШИБКИ НАПРИМЕР,(ИСТЕК СЕРТИФИКАТ, НЕВЕРНЫЙ ПАРОЛЬ)
#! ПРОПУСКАТЬ ТАКИЕ ЭЦП И 'УВЕДОМЛЯТЬ' ОБ ЭТОМ
    def authenticate_proccess(self, selected_path):
        logger.debug(f'path_in_auth={selected_path}')
        """Выполнить авторизацию."""
        try:
            self.state = RobotState.AUTH_STARTED
            logger.info(f"[AUTH STATE CHANGE] Состояние изменено: {self.state.value}")

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
                        file_input = self.driver.find_element(By.XPATH, "//input[@class='custom-file-input']")
                        self.driver.execute_script("arguments[0].style.display = 'block';", file_input)
                        file_input.send_keys(eds_file)
                        logger.debug(f"[AUTH SELECT FILE] Файл выбран: {eds_file}")
                        password_field = self.driver.find_element(By.XPATH, "//input[@type='password' and @class='listBox form-control' and not(@disabled)]")
                        password_field.send_keys(password)
                        self.driver.click_element(By.XPATH, "//button[contains(text(), 'Ok') and not(@disabled)]", "[AUTH CLICK ELEMENT 'OK'] Нажата кнопка 'Ok'")
                        self.driver.click_element(By.XPATH, "//button[contains(text(), 'Выбрать')]", "[AUTH CLICK ELEMENT 'SELECT'] Нажата кнопка 'Выбрать'")
                        
                        #? Перед выходом, робот должен отработать весь необходимый функционал
                        
                        # todo: выход должен быть реализован в конце, как и нажатие на кнопку входа по эцп
                        # self.driver.click_element(By.XPATH, "//a[@title='Выход']", "[END CLICK ELEMENT 'EXIT'] Нажата кнопка 'Выход'")
                        # self.driver.click_element(By.XPATH, "//button[contains(text(), 'Войти по ЭЦП')]", "[START CLICK ELEMENT LOGIN EDS] 'Войти по ЭЦП'", wait_for_visibility=True)

            # --- = --- 

            # Здесь должна быть логика авторизации
            logger.info("[AUTH SUCCESS] Авторизация выполнена успешно")
            self.state = RobotState.AUTH_COMPLETED
            logger.info(f"[AUTH STATE CHANGE] Состояние изменено: {self.state.value}")
        except Exception as Err:
            self.state = RobotState.ERROR
            logger.error(f"[CLASS ROBOT] Ошибка при выполнении authenticate: {Err}")
            #? ---
            self.driver.quit()
            raise

    #! ...
    #! Здесь(между авторизацией и сальдо) должен быть 
    #! реализован обработчик handle_popup
    #! ...

    def balance_personal_accounts(self):
        user_info_loaded = self.driver.wait_for_element(By.XPATH, "//div[contains(@class, 'userInfo')]")

        if user_info_loaded:
            logger.info("[CHECK] Элемент 'userInfo' найден, продолжаем работу")
            self.driver.navigate_to_url(self.BALANCE_PERSONAL_ACCOUNTS_URL)
        else:
            logger.error("[ERROR] Элемент 'userInfo' не найден, возможны проблемы на странице")


        self.driver.click_element(By.XPATH, "(//button[contains(text(), 'Обновить страницу')])[1]", "[BALANCE CLICK ELEMENT 'Обновить страницу'] Нажата кнопка 'Обновить страницу'")
        # self.driver.click_element(
        #     By.XPATH, 
        #     "//button[contains(@class, 'btn-primary') and contains(text(), 'Запросить сальдо ЛС')]", 
        #     "[BALANCE CLICK ELEMENT 'Запросить сальдо ЛС'] Нажата кнопка 'Запросить сальдо ЛС'"
        # )
        # ---=================================================================================--
        #? ПОСЛЕ ЗАПРОСА НА САЛЬДО ВЫЙДЕТ МОДАЛЬНОЕ ОКНО
        #? КОТОРОЕ НУЖНО ПОДТВЕРДИТЬ НАЖАТИЕМ НА КНОПКУ ОК
        #? ИЛИ ОБРАБОТАТЬ ЭТО ОКНО, ЕСЛИ НЕ ПОЯВИТСЯ ОКНО
        # ok_xpath = "//button[contains(@class, 'btn btn-primary') and contains(text(), 'OK')]"
        # close_css = ".modal-content .close"

        # ok_button = self.driver.find_element(By.XPATH, ok_xpath)
        # close_button = self.driver.find_element(By.CSS_SELECTOR, close_css)

        # if ok_button:
        #     self.driver.click_element(By.XPATH, ok_xpath, "[SELENIUM] Нажата кнопка 'OK'")
        # elif close_button:
        #     self.driver.click_element(By.CSS_SELECTOR, close_css, "[SELENIUM] Закрыто модальное окно с ошибкой")
        # else:
        #     logger.error("[ERROR] Ни кнопка 'OK', ни кнопка закрытия не найдены.")

        #? Нахожу элемент до которого буду скролить
        if self.driver.wait_for_element(By.ID, "dataTable"):
            table_balance = self.driver.find_element(By.ID, "dataTable")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", table_balance)
        else:
            logger.error("[BALANCE ERROR] Таблица с сальдо не найдена, возможно, данные не загрузились")


        #? Делаем скриншот вне зависимости от отрицательного значения сальдо
        self.driver.take_screenshot("screenshots")


        exit_button = self.driver.wait_for_element(By.XPATH, "//a[@title='Выход']", timeout=5)
        if exit_button:
            self.driver.click_element(By.XPATH, "//a[@title='Выход']", "[END CLICK] Нажата кнопка 'Выход'")
        else:
            logger.error("[EXIT ERROR] Кнопка 'Выход' не найдена")

        logger.debug('Спи..')
        time.sleep(5)

        logger.info("[BALANCE INFO] Лицевой счет сальдо проверен, процесс завершен")
        

        # time.sleep(1)
        
        # ---=================================================================================--



#! ПОСЛЕ ВХОДА В СИСТЕМУ
#! ОБЯЗАТЕЛЬНО НУЖНО ПРОВЕРИТЬ ПОП-АП ОКНА
