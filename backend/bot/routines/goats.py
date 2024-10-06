import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class GOATSRoutine:
    def __init__(self, settings):
        self.settings = settings
        self.driver = None

    def setup_driver(self):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def run(self):
        try:
            self.setup_driver()
            self.login()
            self.perform_routine()
        except Exception as e:
            logger.error(f"Error in GOATS routine: {str(e)}")
        finally:
            if self.driver:
                self.driver.quit()

    def login(self):
        try:
            self.driver.get("https://web.telegram.org/k/")
            phone_input = self.wait_for_element((By.NAME, "phone_number"))
            phone_input.send_keys(self.settings['phone_number'])
            
            next_button = self.wait_for_element((By.XPATH, "//button[contains(text(), 'Next')]"))
            next_button.click()
            
            # Wait for and enter the confirmation code
            code_input = self.wait_for_element((By.NAME, "phone_code"))
            code_input = input("Enter the confirmation code: ")  # In production, this should be handled differently
            code_input.send_keys(code_input)
            
            submit_button = self.wait_for_element((By.XPATH, "//button[contains(text(), 'Submit')]"))
            submit_button.click()
            
            logger.info("Successfully logged in to Telegram")
        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            raise

    def perform_routine(self):
        try:
            # Navigate to GOATS channel
            self.open_goats_channel()
            
            # Click the launch button
            self.click_launch_button()
            
            # Open missions tab
            self.open_missions_tab()
            
            # Click do button to watch an ad
            self.click_do_button()
            
            # Simulate watching the ad
            self.wait_for_ad()
            
            logger.info("GOATS routine completed successfully")
        except Exception as e:
            logger.error(f"Error during GOATS routine: {str(e)}")
            raise

    def open_goats_channel(self):
        try:
            search_input = self.wait_for_element((By.XPATH, "//input[@placeholder='Search']"))
            search_input.send_keys("GOATS")
            
            channel_link = self.wait_for_element((By.XPATH, "//div[contains(text(), 'GOATS')]"))
            channel_link.click()
            
            logger.info("Opened GOATS channel")
        except Exception as e:
            logger.error(f"Error opening GOATS channel: {str(e)}")
            raise

    def click_launch_button(self):
        try:
            launch_button = self.wait_for_element((By.XPATH, "//button[contains(text(), 'Launch')]"))
            launch_button.click()
            logger.info("Clicked launch button")
        except Exception as e:
            logger.error(f"Error clicking launch button: {str(e)}")
            raise

    def open_missions_tab(self):
        try:
            missions_tab = self.wait_for_element((By.XPATH, "//div[contains(text(), 'Missions')]"))
            missions_tab.click()
            logger.info("Opened missions tab")
        except Exception as e:
            logger.error(f"Error opening missions tab: {str(e)}")
            raise

    def click_do_button(self):
        try:
            do_button = self.wait_for_element((By.XPATH, "//button[contains(text(), 'Do')]"))
            do_button.click()
            logger.info("Clicked do button")
        except Exception as e:
            logger.error(f"Error clicking do button: {str(e)}")
            raise

    def wait_for_ad(self):
        logger.info("Waiting for ad to complete...")
        self.driver.implicitly_wait(18)  # Wait for 18 seconds

    def wait_for_element(self, locator, timeout=10):
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )

# Example usage in a Celery task:
# @celery.task
# def run_goats_routine(settings):
#     routine = GOATSRoutine(settings)
#     routine.run()