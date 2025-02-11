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


class RobotISNA(BaseRobot):
    ISNA_URL = 'https://knp.kgd.gov.kz/signin'


    def navigation_proccess(self):
        """Начать навигацию."""
        try:
            self.state = RobotState.NAVIGATION_STARTED
            logger.info(f"[START STATE CHANGE] Состояние изменено: {self.state.value}")

            self.driver.navigate_to_url(self.ISNA_URL)
            
            self.driver.execute_script(WINDOW_ACTIVITY_SCRIPT)
            logger.info("[START OPEN URL] Открыл сайт: knp.kgd.gov.kz")
            
            self.driver.click_element(By.XPATH, "//button[contains(@class, 'ant-btn button button--gold')]", "[START CLICK ELEMENT LOGIN EDS] 'Выбрать ЭЦП'", wait_for_visibility=True)

            self.state = RobotState.NAVIGATION_COMPLETED
            logger.info(f"[START STATE CHANGE] Состояние изменено: {self.state.value}")
        except Exception as Err:
            self.state = RobotState.ERROR
            logger.error(f"[START CLASS ROBOT] Ошибка при выполнении start_navigation: {Err}")
            self.driver.quit()
            raise

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


                        # --- = --- 
                        #!! явное ожидание пока грузится javaw.rxr окно с выбором эцп
                        # time.sleep(6)
                        # --- = --- 

                        authorize_face(eds_file, password)
                        
                        # --- Ожидание кнопки "Подать документ" ---
                        button_xpath = "//button[contains(@class, 'ant-btn') and contains(@class, 'header__button') and span[text()='Подать документ']]"
                        logger.info("[AUTH] Ожидание кнопки 'Подать документ'")
                        button = self.driver.find_element(By.XPATH, button_xpath)

                        if button:
                            logger.info("[AUTH] Кнопка 'Подать документ' найдена, сайт готов к работе")
                            
                            # --- Наведение на выпадающее меню ---
                            dropdown_xpath = "(//div[contains(@class, 'topbar__item') and contains(@class, 'topbar__dropdown')])[2]"
                            
                            logger.info("[AUTH] Ожидание элемента выпадающего меню")
                            dropdown_element = self.driver.find_element(By.XPATH, dropdown_xpath)

                            if dropdown_element:
                                logger.info("[AUTH] Наведение на элемент выпадающего меню")
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", dropdown_element)
                                ActionChains(self.driver.get_driver()).move_to_element(dropdown_element).perform()
                                logger.info("[AUTH] Наведение на выпадающее меню завершено")

                                # --- Нажатие на ссылку "Выход" ---
                                logout_xpath = "(//div[contains(@class, 'topbar__item') and contains(@class, 'topbar__dropdown')])[2]//a[text()='Выход']"
                                logger.info("[AUTH] Ожидание кнопки 'Выход'")

                                try:
                                    logout_button = self.driver.find_element(By.XPATH, logout_xpath)
                                    logout_button.click()
                                    logger.info("[AUTH] Нажатие на 'Выход' выполнено успешно")

    
                                    self.driver.click_element(By.XPATH, "//button[contains(@class, 'ant-btn button button--gold')]", "[START CLICK ELEMENT LOGIN EDS] 'Выбрать ЭЦП'", wait_for_visibility=True)


                                except Exception as e:
                                    logger.error(f"[AUTH ERROR] Не удалось найти или нажать кнопку 'Выход': {e}")
                            else:
                                logger.error("[AUTH ERROR] Элемент выпадающего меню не найден")
                        else:
                            logger.error("[AUTH ERROR] Кнопка 'Подать документ' не найдена, сайт не готов к работе")
                        
            # --- = --- 

            # Здесь должна быть логика авторизации
            logger.info("[AUTH SUCCESS] Авторизация выполнена успешно")
            self.state = RobotState.AUTH_COMPLETED
            logger.info(f"[AUTH STATE CHANGE] Состояние изменено: {self.state.value}")
            time.sleep(3)
            close_eds_window('Открыть файл')
            # ! --= т.к этап авторизации последний. здесь и ниже я буду закрывать браузер =-- 
            self.driver.quit()
            logger.info(f"[BROWSER CLOSE] Браузер закрыт")

        except Exception as Err:
            self.state = RobotState.ERROR
            logger.error(f"[CLASS ROBOT] Ошибка при выполнении authenticate: {Err}")
            #! открывается окно после выхода из системы это все будете перенесено
            #! Разлогин будет перенесен обязательно 
            #! здесь я закрываю окон после того как селениум нажал на кнопку (смотреть тут, ctrl+f = 'ant-btn button button--gold')
            close_eds_window('Открыть файл')
            #! ---
            self.driver.quit()
            raise
            
        finally:
            close_eds_window('Открыть файл')
            #! ---
            self.driver.quit()
            logger.info(f"[BROWSER CLOSE] Браузер закрыт")




#! ВЫНЕСТИ В ОБЩУЮ УТИЛИТУ
def authorize_face(file_to_path, file_password):
    try:
        logger.debug(f'[AUTH FACE SUCCESS] path={file_to_path}, password={file_password}')
        # Step 1: Активация окна для выбора ЭЦП
        logger.debug('[AUTH] Step 1: Активация окна для выбора ЭЦП')
        window = wait_for_window('Открыть файл')
        if window:
            logger.debug("Активируем окно выбора ЭЦП...")
            window.activate()
            
            logger.debug(f'[AUTH COPY PATH] Копирование пути в буфер обмена {file_to_path}')
            pyperclip.copy(file_to_path)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(.3)
            pyautogui.press('enter')
        else:
            logger.debug("[AUTH WINDOW SELECT EDS NOT FOUND] Окно активации для выбора ЭЦП не найдено")
            return
                
        # Step 2: Ожидание окна ввода пароля
        logger.debug('[AUTH] Step 2: Ожидание окна ввода пароля')
        window = wait_for_window('Формирование ЭЦП в формате XML')
        if window:
            logger.debug('[AUTH PASSWORD WINDOW ACTIVATION] Окно ввода пароля найдено. Активация...')
            window.activate()

            logger.debug(f'[AUTH COPY PASSWORD] Копирование пароля в буфер обмена. Пароль начинается с: {file_password[:2]}**')
            pyperclip.copy(file_password)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(.3)
            logger.debug('[AUTH PASSWORD ENTER] Нажатие Enter для подтверждения пароля')
            pyautogui.press('enter')

            logger.debug('[AUTH SUCCESS] Пароль успешно введён и подтверждён.')
        else:
            logger.info('[AUTH PASSWORD WINDOW NOT FOUND] Окно для ввода пароля не найдено в течение времени ожидания.')
            return
        
        # Step 3: Подтверждение
        window = wait_for_window('Формирование ЭЦП в формате XML')
        if window:
            logger.debug('[AUTH PASSWORD WINDOW ACTIVATION] Окно ввода пароля найдено. Активация...')
            window.activate()

            time.sleep(.3)
            logger.debug('[AUTH SIGN ENTER] Нажатие Enter для подписи')
            pyautogui.press('enter')

            logger.debug('[AUTH SUCCESS] Пароль успешно введён и подтверждён')
        else:
            logger.info('[AUTH PASSWORD WINDOW NOT FOUND] Окно для подписи не найдено в течение времени ожидания')
            return

    except Exception as Err:
        logger.error(f'[AUTH FACE ERROR] Произошла ошибка при авторизации: {Err}')