import logging
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ..base_bot import BaseBot
from ..config import load_config

class GoatsBot(BaseBot):
    def __init__(self, settings):
        super().__init__(settings)
        self.logger = logging.getLogger(__name__)
        self.config = load_config('goats')
        self.setup_driver()
        self.stats = {
            "tasks_completed": 0,
            "rewards_earned": 0,
            "streak": 0,
            "total_runtime": 0,
            "errors_encountered": 0
        }
        self.stop_flag = False

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def run(self):
        start_time = time.time()
        try:
            self.logger.info("Starting Goats routine")
            self.open_telegram()
            self.navigate_to_goats_chat()
            self.launch_web_application()
            self.perform_missions()
            self.logger.info("Goats routine completed successfully")
            return {"status": "success", "message": "Goats routine completed", "stats": self.get_statistics()}
        except Exception as e:
            self.logger.error(f"Error in Goats routine: {str(e)}")
            self.stats["errors_encountered"] += 1
            return {"status": "error", "message": str(e), "stats": self.get_statistics()}
        finally:
            self.stats["total_runtime"] = time.time() - start_time
            self.driver.quit()

    def open_telegram(self):
        self.logger.info("Opening Telegram web")
        try:
            self.driver.get(self.config['telegram_url'])
            WebDriverWait(self.driver, self.config['page_load_timeout']).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            self.logger.error(f"Failed to open Telegram: {str(e)}")
            raise

    def navigate_to_goats_chat(self):
        self.logger.info("Navigating to Goats chat")
        try:
            search_box = WebDriverWait(self.driver, self.config['element_timeout']).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config['search_box_selector']))
            )
            search_box.send_keys(self.config['goats_chat_name'])
            goats_chat = WebDriverWait(self.driver, self.config['element_timeout']).until(
                EC.element_to_be_clickable((By.XPATH, self.config['goats_chat_xpath']))
            )
            goats_chat.click()
        except Exception as e:
            self.logger.error(f"Failed to navigate to Goats chat: {str(e)}")
            raise

    def launch_web_application(self):
        self.logger.info("Launching GOATS web application")
        try:
            launch_button = WebDriverWait(self.driver, self.config['element_timeout']).until(
                EC.element_to_be_clickable((By.XPATH, self.config['launch_button_xpath']))
            )
            launch_button.click()
            WebDriverWait(self.driver, self.config['page_load_timeout']).until(
                EC.presence_of_element_located((By.XPATH, self.config['web_app_container_xpath']))
            )
        except Exception as e:
            self.logger.error(f"Failed to launch web application: {str(e)}")
            raise

    def perform_missions(self):
        self.logger.info("Starting mission cycle")
        while not self.stop_flag:
            try:
                self.navigate_to_missions_tab()
                self.click_do_button()
                self.wait_for_ad()
                self.wait_for_cooldown()
                self.stats["tasks_completed"] += 1
                self.stats["rewards_earned"] += self.config['reward_per_task']
                self.stats["streak"] += 1
            except Exception as e:
                self.logger.error(f"Error in mission cycle: {str(e)}")
                self.stats["errors_encountered"] += 1
                if self.stats["errors_encountered"] >= self.config['max_errors']:
                    self.logger.warning("Max errors reached. Stopping bot.")
                    break
                time.sleep(self.config['error_cooldown'])

    def navigate_to_missions_tab(self):
        self.logger.info("Navigating to Missions tab")
        try:
            missions_tab = WebDriverWait(self.driver, self.config['element_timeout']).until(
                EC.element_to_be_clickable((By.XPATH, self.config['missions_tab_xpath']))
            )
            missions_tab.click()
        except Exception as e:
            self.logger.error(f"Failed to navigate to Missions tab: {str(e)}")
            raise

    def click_do_button(self):
        self.logger.info("Clicking Do button")
        try:
            do_button = WebDriverWait(self.driver, self.config['element_timeout']).until(
                EC.element_to_be_clickable((By.XPATH, self.config['do_button_xpath']))
            )
            do_button.click()
        except Exception as e:
            self.logger.error(f"Failed to click Do button: {str(e)}")
            raise

    def wait_for_ad(self):
        self.logger.info("Waiting for ad to complete")
        time.sleep(self.config['ad_duration'])

    def wait_for_cooldown(self):
        self.logger.info("Waiting for cooldown")
        time.sleep(self.config['cooldown_duration'])
        self.refresh_missions_tab()

    def refresh_missions_tab(self):
        self.logger.info("Refreshing missions tab")
        try:
            home_tab = WebDriverWait(self.driver, self.config['element_timeout']).until(
                EC.element_to_be_clickable((By.XPATH, self.config['home_tab_xpath']))
            )
            home_tab.click()
            time.sleep(self.config['tab_switch_delay'])
            self.navigate_to_missions_tab()
        except Exception as e:
            self.logger.error(f"Failed to refresh missions tab: {str(e)}")
            raise

    def get_statistics(self):
        return self.stats

    def stop(self):
        self.logger.info("Stopping Goats bot")
        self.stop_flag = True