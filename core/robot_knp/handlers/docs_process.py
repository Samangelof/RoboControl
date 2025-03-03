import time
from selenium.webdriver.common.by import By
from settings.logger import setup_logger
from core.services.utils.common_utils import escape_xpath_text
from core.robot_knp.handlers.pop_up_process import handle_no_data_popup


logger = setup_logger(__name__)
  
  
class DocsProcess:
    def __init__(self, driver):
        self.driver = driver

    def _check_user_info(self):
        """Проверка наличия информации о пользователе."""
        if not self.driver.wait_for_element(By.XPATH, "//div[contains(@class, 'userInfo')]", timeout=20):
            logger.error("[ERROR] Элемент 'userInfo' не найден, остановка выполнения")
            return False
        
        logger.info("[CHECK USERINFO] Элемент 'userInfo' найден, продолжаем работу")
        return True

    def _click_search_button(self):
        """Клик по кнопке 'Найти'"""
        if not self.driver.click_element(By.XPATH, "//button[contains(text(), 'Найти')]"):
            logger.error("[DOCS BUTTON ERROR] Кнопка 'Найти' не нажата")
            return False
        
        logger.info("[BUTTON SEARCH] Нажата кнопка 'Найти'")
        return True

    def _get_documents_table(self):
        """Получение таблицы документов"""
        table = self.driver.wait_for_element(By.ID, "appModalTable", timeout=20)
        if not table:
            logger.error("[DOCS TABLE ERROR] Таблица документов не загрузилась")
            return None
        
        logger.info(f"[TABLE INNER HTML] {table.get_attribute('innerHTML')}")
        return table

    def _process_document_row(self, row):
        """Обработка одной строки таблицы документов"""
        try:
            td_elements = row.find_elements(By.TAG_NAME, "td")
            if len(td_elements) < 5:
                logger.warning(f"[DOCS PROCESS WARNING] В строке недостаточно колонок: {len(td_elements)}")
                return
        
            doc_cell = td_elements[4]
            link_element = doc_cell.find_elements(By.TAG_NAME, "a")
            button_element = doc_cell.find_elements(By.TAG_NAME, "button")

            if link_element:
                self._process_link_document(link_element[0])
                
            elif button_element:
                button_text = button_element[0].text.strip()
                safe_text = escape_xpath_text(button_text)
                button_xpath = f".//button[contains(text(), {safe_text})]"
                
                logger.info(f"[DOCS BUTTON FOUND] Найден документ с кнопкой: {button_text}")
                self._process_button_document(button_xpath)
                
        except Exception as err:
            logger.error(f"[DOCS PROCESS ERROR] Ошибка при обработке строки: {err}")

    def _process_link_document(self, link_element):
        """Обработка документа со ссылкой"""
        doc_url = link_element.get_attribute("href")
        doc_text = link_element.text
        logger.info(f"[DOCS LINK FOUND] Найден документ: {doc_text}")
        
        self.driver.execute_script("window.open(arguments[0]);", doc_url)
        self.driver.switch_to_last_tab()
        
        try:
            print_button = self.driver.wait_for_element(
                By.XPATH, "//div[@class='print-button mb-3 no-print']/input[@type='button' and @value='Печать']", 
                timeout=10
            )
            if print_button:
                print_button.click()
                time.sleep(2)
                logger.info("[DOCS CLICK PRINT] Нажата кнопка 'Печать'")
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                self.driver.execute_script('window.print();')
                logger.info("[DOCS CLICK NOT FOUND PRINT] Кнопка 'Печать' не найдена, выполнена команда 'window.print()'")
        finally:
            self.driver.switch_to_window(0)

    def _process_button_document(self, btn_xpath):
        """Обработка документа с кнопкой"""
        logger.info(f"[DOCS BUTTON FOUND] Используем XPath кнопки: {btn_xpath}")

        #? Две попытки, если появится окно об (Отсутствии сведения по запросу)
        for attempt in range(2):
            self.driver.click_element(By.XPATH, btn_xpath, log_message=f"[DOC CLICKED] Кликнули на документ, попытка {attempt + 1}")
            if not handle_no_data_popup():
                break
            logger.warning("[DOCS WARNING] Окно 'Отсутствуют сведения по запросу' появилось, повторяем попытку")
        else:
            logger.error("[DOCS ERROR] Данные отсутствуют дважды, пропускаем документ")
            # Выход из метода, если окно появилось два раза
            return
        try:
            # появление модального окна
            self.driver.wait_for_element(By.CLASS_NAME, "modal-content")
            logger.info("[MODAL OPENED] Модальное окно найдено")

            # кнопка "Печать" в модальном окне
            self.driver.click_element(By.XPATH, ".//button[contains(text(), 'Печать')]", 
                            log_message="[PRINT CLICKED] Кликнули 'Печать'", 
                            wait_for_visibility=True)

            # кнопка "Отмена" через твой метод
            self.driver.click_element(By.XPATH, ".//button[contains(text(), 'Отмена')]", 
                            log_message="[CANCEL CLICKED] Кликнули 'Отмена', закрываем модальное окно", 
                            wait_for_visibility=True)

            # ---======================================================================================--
            self.driver.refresh()
            logger.info("[PAGE REFRESH] Страница перезагружена")

            if not self._check_user_info():
                logger.warning("[PAGE LOAD] Не удалось убедиться, что страница загрузилась")
                return

            # Повторное нажатие на кнопку "Найти"
            if not self._click_search_button():
                logger.warning("[DOCS SEARCH] Не удалось нажать кнопку 'Найти' после обновления")
                return
            
            # Ожидание таблицы с документами
            if not self.driver.wait_for_element(By.TAG_NAME, "table", timeout=15):
                logger.warning("[DOCS TABLE WAIT] Таблица не появилась после повторного поиска")
                return
            # ---======================================================================================--

        except Exception as err:
            logger.error(f"[MODAL ERROR] Ошибка при работе с модальным окном: {err}")

        finally:
            self.driver.switch_to_window(0)