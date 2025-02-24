import time
from selenium.webdriver.common.by import By
from settings.logger import setup_logger


logger = setup_logger(__name__)
  
  
class DocsProcess:
    def __init__(self, driver):
        self.driver = driver

    def _check_user_info(self):
        """Проверка наличия информации о пользователе."""
        if not self.driver.wait_for_element(By.XPATH, "//div[contains(@class, 'userInfo')]", timeout=10):
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
        table = self.driver.wait_for_element(By.ID, "appModalTable", timeout=10)
        if not table:
            logger.error("[DOCS TABLE ERROR] Таблица документов не загрузилась")
            return None
        
        logger.info(f"[TABLE INNER HTML] {table.get_attribute('innerHTML')}")
        return table

    def _process_document_row(self, row):
        """Обработка одной строки таблицы документов"""
        try:
            doc_cell = row.find_elements(By.TAG_NAME, "td")[4]
            link_element = doc_cell.find_elements(By.TAG_NAME, "a")
            button_element = doc_cell.find_elements(By.TAG_NAME, "button")

            if link_element:
                self._process_link_document(link_element[0])
            elif button_element:
                logger.info(f"[DOCS BUTTON FOUND] Найден документ с кнопкой: {button_element[0].text}")
                
                #!!!!
                # Здесь логика обработки документа с кнопкой
                #!!!!

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
