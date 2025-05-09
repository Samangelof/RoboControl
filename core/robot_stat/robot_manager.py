# core/robot_stat/robot_manager.py
import time 
import pygetwindow as gw
import pyautogui
import pyperclip
from core.services.robot_dependencies.selenium_scripts import WINDOW_ACTIVITY_SCRIPT
from selenium.webdriver.common.by import By
from core.services.utils.common_utils import (
    wait_for_window,
    close_eds_window,
    find_eds_file_and_password
)
from settings.logger import setup_logger
from core.base_robot import BaseRobot


logger = setup_logger(__name__)


class RobotStat(BaseRobot):
    KNP_URL = 'https://cabinet.stat.gov.kz/'

    def navigation_proccess(self):
        """Выполнить навигацию"""
        try:
            self.driver.navigate_to_url(self.KNP_URL)
            
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
        logger.debug(f'path_in_auth={selected_path}')

        try:
            # self.state = RobotState.AUTH_STARTED
            # logger.info(f"[AUTH STATE CHANGE] Состояние изменено: {self.state.value}")

            # Получаю файл ЭЦП и пароль
            eds_file, password = find_eds_file_and_password(selected_path)

            if eds_file and password:
                authorize_face(eds_file, password)
            else:
                logger.error("[AUTH ERROR] Файл ЭЦП или пароль не найдены")
        
        except Exception as e:
            logger.error(f"[AUTH ERROR] Произошла ошибка при авторизации: {e}")

    def reports_proccess(self):
        self.driver.click_element(By.XPATH, '//span[@class="x-tab-inner x-tab-inner-center" and text()="Мои отчёты"]')



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

def authorize_face(file_to_path, file_password):
    try:
        logger.debug(f'[AUTH FACE SUCCESS] path={file_to_path}, password={file_password[:2]}***')

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
            raise Exception("Окно подтверждения подписи не найдено")

    except Exception as Err:
        logger.error(f'[AUTH FACE ERROR] Произошла ошибка при авторизации: {Err}')
        raise