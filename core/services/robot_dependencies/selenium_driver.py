from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
    WebDriverException,
)
from threading import Lock
import time
import os
from datetime import datetime
import json
import pathlib
from settings.logger import setup_logger


logger = setup_logger(__name__)


class SeleniumDriver:
    def __init__(self, headless: bool = False, wait_time: int = 30, save_path: str = None):
        self.driver = None
        self.headless = headless  # Режим без интерфейса (headless)
        self.wait_time = wait_time  # Время ожидания для поиска элементов
        self._lock = Lock()

        # создает папку только если передан save_path
        if save_path:
            self.save_path = pathlib.Path(save_path).resolve()
            self.save_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"[SETUP SAVE PATH] Директория для сохранения файлов: {self.save_path}")
        else:
            # В случае если путь не задан
            self.save_path = None



    def _configure_driver(self) -> webdriver.Chrome:
        """Настройка и запуск драйвера с использованием Remote Debugging"""
        chrome_options = Options()

        settings = {
            "recentDestinations": [{
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }],
            "selectedDestinationId": "Save as PDF",
            "version": 2
        }


        prefs = {
            'printing.print_preview_sticky_settings.appState': json.dumps(settings),
            'savefile.default_directory': str(self.save_path),
        }

        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--kiosk-printing')

        if self.headless:
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-features=IsolateOrigins")
            chrome_options.add_argument("--disable-features=SitePerProcess")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-update")

            #* User-Agent идентифицирует браузер перед сервером
            #? это заголовок от обычного десктопного Chrome 114
            #? Если нужен настоящий, можно взять наш:
            #? Открыть DevTools (F12) → вкладка Network
            #? Выбрать любой запрос и найти заголовок User-Agent
            #? Подставить его в код, чтобы Selenium выглядел как наш браузер
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36")

        start_time = time.time()
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.maximize_window()
            end_time = time.time()
            logger.info(f"Время запуска браузера: {end_time - start_time:.2f} секунд")
        except Exception as e:
            logger.error(f"Ошибка при запуске драйвера: {e}")
            raise e
        return driver

    def get_driver(self) -> webdriver.Chrome:
        with self._lock:
            if not self.driver:
                logger.info("[SETUP DRIVE] Настройка драйвера")
                self.driver = self._configure_driver()
        return self.driver

    def quit(self):
        """Закрытие браузера."""
        if self.driver:
            logger.info("[CLOSE DRIVER] Закрытие браузера")
            self.driver.quit()
            self.driver = None
        else:
            logger.warning("Попытка закрыть браузер, но драйвер не был инициализирован (скорее всего уже закрыт)")

    def navigate_to_url(self, url: str):
        """Переход по URL с обработкой ошибок."""
        try:
            logger.info(f"Переход по URL: {url}")
            self.get_driver().get(url)
        except Exception as e:
            logger.error(f"Ошибка при переходе на URL {url}: {e}")
            raise
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Ожидает появления элемента на странице в течении 10 секунд"""
        timeout = timeout or self.wait_time
        try:
            element = WebDriverWait(self.get_driver(), timeout).until(
                EC.presence_of_element_located((by, value))
            )
            logger.info(f"[WAIT] Элемент найден: {value}")
            return element
        except TimeoutException:
            logger.warning(f"[WAIT] Элемент не появился за {timeout} секунд: {value}")
            return None
            


    def find_element(self, by: By, value: str, wait_time=15):
        """Поиск элемента с ожиданием"""
        try:
            logger.info(f"Поиск элемента: {value}")
            return WebDriverWait(self.get_driver(), wait_time).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            logger.debug(f"Элемент не найден: {value}")
            return None
        except Exception as e:
            logger.debug(f"Ошибка при поиске элемента {value}: {e}")
            return None

    def find_elements(self, by: By, value: str):
        """Поиск элементов с ожиданием"""
        try:
            logger.info(f"[SEARCH ELEMENTS] Поиск элементов: {value}")
            return WebDriverWait(self.get_driver(), self.wait_time).until(
                EC.presence_of_all_elements_located((by, value))
            )
        except Exception as e:
            logger.error(f"Ошибка при поиске элементов {value}: {e}")
            return []


    def click_element(self, by: By, value: str, log_message: str = None, wait_for_visibility: bool = False):
        """
        Универсальный клик по элементу с обработкой видимости и кликабельности
        
        :param by: Тип селектора (например, By.XPATH, By.ID)
        :param value: Значение селектора
        :param log_message: Сообщение для логирования при успешном клике (опционально)
        :param wait_for_visibility: Если True, сначала ждёт видимости элемента
        """
        try:
            logger.info(f"Ожидание элемента: {value}")
            
            # видимость элемента, если указано
            if wait_for_visibility:
                element = WebDriverWait(self.get_driver(), self.wait_time).until(
                    EC.visibility_of_element_located((by, value))
                )
            else:
                # кликабельность элемента
                element = WebDriverWait(self.get_driver(), self.wait_time).until(
                    EC.element_to_be_clickable((by, value))
                )
            
            logger.info(f"Клик по элементу: {value}")
            
            # element.click()
            # Использую клик по элементам через js, т.к selenium может не видеть элементы
            try:
                element.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", element)

            if log_message:
                logger.info(log_message)

            return True
        except NoSuchElementException:
            logger.error(f"[ERROR] Элемент с селектором '{value}' не найден.")
        except ElementClickInterceptedException:
            logger.error(f"[ERROR] Клик по элементу '{value}' перехвачен другим элементом.")
        except TimeoutException:
            logger.error(f"[ERROR] Тайм-аут ожидания элемента '{value}'.")
        except WebDriverException as e:
            logger.error(f"[ERROR] WebDriver ошибка при взаимодействии с элементом '{value}': {str(e)}")
        except Exception as e:
            logger.error(f"[ERROR] Неизвестная ошибка при клике по элементу '{value}': {str(e)}")
            return False

    def send_keys(self, by: By, value: str, keys: str):
        """Отправка текста в поле ввода"""
        element = self.find_element(by, value)
        if element:
            logger.info(f"Отправка текста '{keys}' в поле {value}")
            element.send_keys(keys)
        else:
            logger.error(f"Не удалось отправить текст в поле {value}")

    #! Переработать указана хардкодная папка со скринам
    #! (обсуждаемо) у каждой эцп, своя папка в которая хранятся все данные 
    def take_screenshot(self, name: str = "screenshot", folder: str="screenshots"):
        """Сохраняет скриншот текущего экрана в папку screenshots/"""
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = f"{folder}/{name}_{timestamp}.png"

        try:
            self.get_driver().save_screenshot(filepath)
            logger.info(f"[SCREENSHOT] Скриншот сохранён: {filepath}")
        except Exception as e:
            logger.error(f"[ERROR SCREENSHOT] Ошибка при сохранении скриншота: {e}")
            
    def execute_script(self, script: str, *args):
        """Выполнение JavaScript-скрипта в текущем контексте страницы"""
        try:
            logger.info(f"[EXECUTE SCRIPT] Выполнение скрипта: {script[:40]}...")
            return self.get_driver().execute_script(script, *args)
        except Exception as e:
            logger.error(f"[ERROR EXECUTE SCRIPT] Ошибка при выполнении скрипта: {e}")
            raise

    def switch_to_window(self, index):
        """Переключение вкладки по индексу"""
        try:
            self.driver.switch_to.window(self.driver.window_handles[index]) 
            logger.info(f"[TAB SWITCH] Переключился на вкладку с индексом {index}")
        except IndexError:
            logger.error(f"[TAB SWITCH ERROR] Вкладка с индексом {index} не найдена")

    def switch_to_last_tab(self):
        """Переключение на последнюю открытую вкладку"""
        try:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            logger.info("[TAB SWITCH] Переключился на последнюю вкладку")
        except IndexError:
            logger.error("[TAB SWITCH ERROR] Нет открытых вкладок для переключения")

    def refresh(self):
        try:
            self.driver.refresh()
            logger.info("[SELENIUM] Страница успешно перезагружена.")
        except Exception as e:
            logger.error(f"[ERROR] Ошибка при перезагрузке страницы: {e}")