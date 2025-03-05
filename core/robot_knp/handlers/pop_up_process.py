from selenium.webdriver.common.by import By
from settings.logger import setup_logger


logger = setup_logger(__name__)
  

def handle_no_data_popup(driver):
    """Обрабатывает окно 'Отсутствуют сведения по запросу'."""
    popup_xpath = "//div[contains(@class, 'modal-body') and contains(text(), 'Отсутствуют сведения по запросу')]"
    cancel_button_xpath = "//button[contains(@class, 'btn-secondary') and text()='Отмена']"

    if driver.wait_for_element(By.XPATH, popup_xpath, timeout=3):
        logger.info("[POPUP] Обнаружено сообщение 'Отсутствуют сведения по запросу'")

        cancel_button = driver.find_element(By.XPATH, cancel_button_xpath)
        cancel_button.click()
        logger.info("[POPUP] Нажата кнопка 'Отмена'")
        
        return True

    return False
