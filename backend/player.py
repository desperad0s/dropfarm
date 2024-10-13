import time
import logging
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .automation_config import get_chrome_driver

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Player:
    def __init__(self, routine_name, actions, repeat_indefinitely=False):
        self.routine_name = routine_name
        self.actions = actions
        self.driver = None
        self.start_time = None
        self.is_playing = False
        self.repeat_indefinitely = repeat_indefinitely
        self.stop_requested = False

    def start(self):
        self.driver = get_chrome_driver()
        self.driver.get('https://web.telegram.org/k/')
        logger.info(f"Started player for routine: {self.routine_name}")
        
        self.driver.maximize_window()
        self.driver.fullscreen_window()
        
        self.setup_ui()
        self.setup_start_trigger()
        self.wait_for_start_signal()

    def setup_ui(self):
        js_code = """
        var statusDiv = document.createElement('div');
        statusDiv.id = 'playback-status';
        statusDiv.style.position = 'fixed';
        statusDiv.style.top = '10px';
        statusDiv.style.left = '10px';
        statusDiv.style.padding = '10px';
        statusDiv.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        statusDiv.style.color = 'white';
        statusDiv.style.zIndex = '9999999';
        statusDiv.innerHTML = 'Press 9 to start playback';
        document.body.appendChild(statusDiv);
        """
        self.driver.execute_script(js_code)

    def setup_start_trigger(self):
        js_code = """
        document.addEventListener('keydown', function(e) {
            if (e.key === '9') {
                window.dispatchEvent(new CustomEvent('startPlayback'));
                document.getElementById('playback-status').innerHTML = 'Playback started';
            }
        });
        """
        self.driver.execute_script(js_code)

    def wait_for_start_signal(self):
        logger.info("Waiting for '9' key press to start playback...")
        self.driver.execute_script("""
        window.playbackStarted = false;
        window.addEventListener('startPlayback', function() {
            window.playbackStarted = true;
        });
        """)
        
        try:
            WebDriverWait(self.driver, 600).until(
                lambda d: d.execute_script("return window.playbackStarted === true;")
            )
        except TimeoutException:
            logger.info("Playback start timed out after 10 minutes.")
            return
        
        logger.info("Playback start signal received.")
        self.start_time = time.time()
        self.is_playing = True
        self.play()

    def play(self):
        if not self.actions['actions']:
            logger.warning("No actions to play")
            return

        while self.is_playing and not self.stop_requested:
            self.start_time = time.time()
            last_action_time = 0
            for action in self.actions['actions']:
                if self.stop_requested:
                    break
                self.wait_for_action_time(action['time'])
                if action['type'] == 'click':
                    self.perform_click(action['x'], action['y'])
                last_action_time = action['time']
            
            # Handle final wait time
            final_wait_time = max(0, last_action_time - (time.time() - self.start_time))
            if final_wait_time > 0:
                logger.info(f"Waiting for final delay of {final_wait_time:.2f} seconds")
                time.sleep(final_wait_time)
            
            if not self.repeat_indefinitely:
                break
            
            time.sleep(1)  # Small delay before next iteration

        logger.info("Playback completed")
        self.driver.execute_script("document.getElementById('playback-status').innerHTML = 'Playback completed';")

    def wait_for_action_time(self, action_time):
        current_time = time.time() - self.start_time
        wait_time = max(0, action_time - current_time)
        if wait_time > 0:
            logger.debug(f"Waiting for {wait_time:.2f} seconds before next action")
            time.sleep(wait_time)

    def perform_click(self, x, y):
        window_size = self.driver.get_window_size()
        actual_x = int(x * window_size['width'])
        actual_y = int(y * window_size['height'])
        logger.info(f"Clicking at relative position ({x}, {y}), actual position ({actual_x}, {actual_y})")
        self.show_click_indicator(actual_x, actual_y)
        
        actions = ActionChains(self.driver)
        actions.move_by_offset(actual_x, actual_y).click().perform()
        actions.move_by_offset(-actual_x, -actual_y).perform()  # Reset mouse position

    def show_click_indicator(self, x, y):
        js_code = """
        var clickIndicator = document.createElement('div');
        clickIndicator.style.position = 'fixed';
        clickIndicator.style.left = arguments[0] + 'px';
        clickIndicator.style.top = arguments[1] + 'px';
        clickIndicator.style.width = '10px';
        clickIndicator.style.height = '10px';
        clickIndicator.style.borderRadius = '50%';
        clickIndicator.style.backgroundColor = 'rgba(0, 255, 0, 0.5)';
        clickIndicator.style.zIndex = '9999';
        document.body.appendChild(clickIndicator);
        setTimeout(function() {
            clickIndicator.remove();
        }, 2000);
        """
        self.driver.execute_script(js_code, x, y)

    def stop(self):
        self.stop_requested = True
        self.is_playing = False
        if self.driver:
            self.driver.quit()
        logger.info(f"Stopped playback for routine: {self.routine_name}")

def start_playback(routine_name, actions, repeat_indefinitely=False):
    logger.info(f"Starting {'repeat' if repeat_indefinitely else 'solo'} playback for routine: {routine_name}")
    logger.info(f"Number of actions: {len(actions['actions'])}")
    logger.info(f"Repeat: {repeat_indefinitely}")
    player = Player(routine_name, actions, repeat_indefinitely)
    player.start()
    return player
